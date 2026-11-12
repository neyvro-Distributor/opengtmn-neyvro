#!/usr/bin/env python3
"""Run the real local MCP gateway against the real local AWS API.

This runner is deliberately conservative: it only accepts loopback URLs,
never prints bearer tokens, and returns a blocked report instead of replacing
an unavailable backend with mocks.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from neyvro.remote_mcp import ENABLED_PRIVATE_TOOLS, OPERATION_ADAPTERS, SPEC_BY_NAME, TOOL_OPERATION_MAP  # noqa: E402

EXPECTED_OPERATIONS = {
    "companies.search", "companies.get", "companies.people", "buyers.search", "signals.list",
    "opportunities.list", "opportunities.get", "objective.get", "brief.get", "pipeline.get",
    "analytics.get", "conversations.list", "conversations.get", "mail.overview",
}
UUID = "00000000-0000-0000-0000-000000000001"


@dataclass
class CallResult:
    tool: str
    operation: str
    status: str
    http_status: int | None = None
    error_code: str | None = None


def _loopback(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and parsed.hostname in {"127.0.0.1", "localhost", "::1"}


def _safe_json(response: httpx.Response) -> dict:
    try:
        value = response.json()
        return value if isinstance(value, dict) else {}
    except (ValueError, TypeError):
        return {}


def _rpc_payload(response: httpx.Response) -> dict:
    if "text/event-stream" not in response.headers.get("content-type", ""):
        return _safe_json(response)
    for line in response.text.splitlines():
        if line.startswith("data:"):
            try:
                value = json.loads(line[5:].strip())
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                return value
    return {}


def _tool_arguments(tool: str) -> dict:
    spec = SPEC_BY_NAME[tool]
    args: dict[str, object] = {}
    for field in spec.required_fields:
        args[field] = UUID
    if tool == "neyvro_get_buyer":
        args["buyer_id"] = UUID
    if tool == "neyvro_get_followup_queue":
        args["filter"] = "waiting"
    return args


def _error_code(payload: dict) -> str | None:
    error = payload.get("error")
    if isinstance(error, dict):
        data = error.get("data")
        if isinstance(data, dict) and isinstance(data.get("code"), str):
            return data["code"]
    result = payload.get("result")
    if isinstance(result, dict):
        structured = result.get("structuredContent")
        if isinstance(structured, dict):
            nested = structured.get("error")
            if isinstance(nested, dict) and isinstance(nested.get("code"), str):
                return nested["code"]
    return None


def _mark_blocked(report: dict, reason: str) -> None:
    blockers = report.setdefault("blockers", [])
    if reason not in blockers:
        blockers.append(reason)
    if not report["tool_results"]:
        report["tool_results"] = [{"tool": tool, "operation": TOOL_OPERATION_MAP[tool], "status": "BLOCKED", "http_status": None, "error_code": "prerequisite_unavailable"} for tool in sorted(ENABLED_PRIVATE_TOOLS)]


def run(args: argparse.Namespace) -> dict:
    expected_tools = sorted(ENABLED_PRIVATE_TOOLS)
    report: dict = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "identity_mode": os.getenv("NEYVRO_E2E_IDENTITY_MODE", "not_configured"),
        "gateway": args.gateway,
        "backend": args.backend,
        "source": {"render_base": "codex/mcp-auth-scope-grants", "aws_revision": "3aca5d1"},
        "contract": {"expected_operations": len(EXPECTED_OPERATIONS), "expected_tools": len(expected_tools)},
        "prerequisites": {},
        "tool_results": [],
        "status": "BLOCKED",
    }
    report["contract"]["operation_registry_match"] = set(OPERATION_ADAPTERS) == EXPECTED_OPERATIONS
    if not _loopback(args.gateway) or not _loopback(args.backend):
        report["prerequisites"]["loopback_targets"] = "FAIL"
        _mark_blocked(report, "Only loopback gateway and backend URLs are permitted.")
        return report
    token = os.getenv(args.token_env, "")
    report["prerequisites"]["token_a_present"] = bool(token)
    try:
        with httpx.Client(timeout=args.timeout, follow_redirects=False) as client:
            for name, url in (("gateway_health", f"{args.gateway.rstrip('/')}/health"), ("backend_health", f"{args.backend.rstrip('/')}/health")):
                try:
                    response = client.get(url)
                    report["prerequisites"][name] = {"status": response.status_code, "reachable": True}
                except httpx.HTTPError as exc:
                    report["prerequisites"][name] = {"reachable": False, "error": type(exc).__name__}
            if not report["prerequisites"].get("token_a_present"):
                report["blockers"] = [f"Set {args.token_env} to a real test identity token; no token was read."]
            if not report["prerequisites"].get("gateway_health", {}).get("reachable") or not report["prerequisites"].get("backend_health", {}).get("reachable"):
                report["blockers"] = report.get("blockers", []) + ["Both local gateway and AWS API must be reachable before real MCP calls."]
            if report.get("blockers"):
                if not report["prerequisites"].get("gateway_health", {}).get("reachable") or not report["prerequisites"].get("backend_health", {}).get("reachable"):
                    _mark_blocked(report, "Both local gateway and AWS API must be reachable before real MCP calls.")
                else:
                    _mark_blocked(report, report["blockers"][0])
                return report

            headers = {"Authorization": f"Bearer {token}", "Accept": "application/json, text/event-stream", "Content-Type": "application/json", "MCP-Protocol-Version": "2025-06-18"}
            session_id = None
            def rpc(method: str, request_id: int | None, params: dict | None = None) -> tuple[httpx.Response, dict]:
                nonlocal session_id
                body = {"jsonrpc": "2.0", "method": method}
                if request_id is not None:
                    body["id"] = request_id
                if params is not None:
                    body["params"] = params
                response = client.post(f"{args.gateway.rstrip('/')}/mcp", headers=headers, json=body)
                session_id = response.headers.get("mcp-session-id", session_id)
                if session_id:
                    headers["Mcp-Session-Id"] = session_id
                return response, _rpc_payload(response)

            init_response, init_payload = rpc("initialize", 1, {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "neyvro-real-e2e", "version": "1"}})
            report["mcp_initialize"] = {"http_status": init_response.status_code, "jsonrpc_error": bool(init_payload.get("error"))}
            rpc("notifications/initialized", None)
            list_response, list_payload = rpc("tools/list", 2, {})
            advertised = {item.get("name") for item in list_payload.get("result", {}).get("tools", []) if isinstance(item, dict)}
            report["tools_list"] = {"http_status": list_response.status_code, "advertised_private_tools": len(advertised & set(expected_tools)), "missing_private_tools": sorted(set(expected_tools) - advertised)}
            if list_response.status_code >= 400 or not advertised:
                _mark_blocked(report, "MCP tools/list did not return a usable private-tool catalog.")
                return report
            for tool in expected_tools:
                response, payload = rpc("tools/call", 1000 + len(report["tool_results"]), {"name": tool, "arguments": _tool_arguments(tool)})
                result = CallResult(tool, TOOL_OPERATION_MAP[tool], "PASS" if response.status_code < 400 and not payload.get("error") else "ERROR", response.status_code, _error_code(payload))
                report["tool_results"].append(result.__dict__)
    except httpx.HTTPError as exc:
        _mark_blocked(report, f"Local MCP HTTP failure: {type(exc).__name__}")
        return report
    report["status"] = "PASS" if all(item["status"] == "PASS" for item in report["tool_results"]) else "FAIL"
    return report


def _write_markdown(report: dict, path: str) -> None:
    lines = ["# NEYVRO real local MCP E2E", "", f"Status: **{report['status']}**", "", "## Prerequisites", "", "| Check | Result |", "|---|---|"]
    for name, result in report.get("prerequisites", {}).items():
        lines.append(f"| `{name}` | `{json.dumps(result, sort_keys=True)}` |" )
    lines += ["", "## Tool results", "", "| Tool | Operation | Status | HTTP | Error |", "|---|---|---|---:|---|"]
    for item in report.get("tool_results", []):
        lines.append(f"| `{item['tool']}` | `{item['operation']}` | `{item['status']}` | {item.get('http_status') or ''} | {item.get('error_code') or ''} |")
    if report.get("blockers"):
        lines += ["", "## Blockers", ""] + [f"- {blocker}" for blocker in report["blockers"]]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gateway", default="http://127.0.0.1:8000")
    parser.add_argument("--backend", default="http://127.0.0.1:8001")
    parser.add_argument("--token-env", default="NEYVRO_E2E_TOKEN_A")
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("--json", default="/tmp/neyvro-mcp-real-e2e.json")
    parser.add_argument("--markdown", default="/tmp/neyvro-mcp-real-e2e.md")
    args = parser.parse_args()
    report = run(args)
    Path(args.json).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_markdown(report, args.markdown)
    print(json.dumps({"status": report["status"], "json_report": args.json, "markdown_report": args.markdown, "prerequisites": report["prerequisites"]}, sort_keys=True))
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
