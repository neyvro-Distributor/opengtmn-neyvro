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
from uuid import UUID as UUIDType

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from neyvro.remote_mcp import CONTRACT_OPERATIONS, ENABLED_PRIVATE_TOOLS, OPERATION_ADAPTERS, SPEC_BY_NAME, TOOL_OPERATION_MAP  # noqa: E402

EXPECTED_OPERATIONS = {
    "companies.search", "companies.get", "companies.people", "buyers.search", "signals.list",
    "opportunities.list", "opportunities.get", "objective.get", "brief.get", "pipeline.get",
    "analytics.get", "conversations.list", "conversations.get", "mail.overview",
}
POSITIVE_STATUSES = {"available"}
DENIAL_STATUSES = {
    "unauthorized", "forbidden", "disabled", "insufficient_scope", "not_found",
    "invalid_request", "backend_unavailable", "rate_limited", "pending_approval",
    "workspace_selection_required", "not_ready",
}
SENSITIVE_MARKERS = ("bearer ", "eyj", "private_key", "access_token", "refresh_token")


@dataclass
class CallResult:
    tool: str
    operation: str
    status: str
    http_status: int | None = None
    error_code: str | None = None
    classification: str = "FAIL_PROTOCOL"
    detail: str | None = None


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


def _valid_uuid(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return str(UUIDType(value)) == value and value == value.lower()
    except ValueError:
        return False


@dataclass
class ResourceCatalog:
    workspace_id: str | None = None
    company_id: str | None = None
    buyer_id: str | None = None
    opportunity_id: str | None = None
    conversation_id: str | None = None


def _find_uuid(value: object, preferred: tuple[str, ...]) -> str | None:
    if isinstance(value, dict):
        for key in preferred:
            candidate = value.get(key)
            if _valid_uuid(candidate):
                return candidate
        for nested in value.values():
            found = _find_uuid(nested, preferred)
            if found:
                return found
    elif isinstance(value, list):
        for nested in value:
            found = _find_uuid(nested, preferred)
            if found:
                return found
    return None


def _catalog_from_result(payload: dict, catalog: ResourceCatalog) -> ResourceCatalog:
    structured = payload.get("result", {}).get("structuredContent", {})
    data = structured.get("data", structured) if isinstance(structured, dict) else {}
    for field, keys in {
        "workspace_id": ("workspace_id",),
        "company_id": ("company_id", "id"),
        "buyer_id": ("buyer_id", "person_id", "id"),
        "opportunity_id": ("opportunity_id", "id"),
        "conversation_id": ("conversation_id", "id"),
    }.items():
        if getattr(catalog, field) is None:
            found = _find_uuid(data, keys)
            if found:
                setattr(catalog, field, found)
    return catalog


def _schema_properties(schema: dict) -> dict:
    properties = schema.get("properties") if isinstance(schema, dict) else None
    return properties if isinstance(properties, dict) else {}


def _value_for_field(field: str, catalog: ResourceCatalog) -> object:
    values = {
        "workspace_id": catalog.workspace_id,
        "company_id": catalog.company_id,
        "buyer_id": catalog.buyer_id,
        "opportunity_id": catalog.opportunity_id,
        "conversation_id": catalog.conversation_id,
        "query": "example",
        "page": 1,
        "page_size": 25,
        "offset": 0,
        "limit": 25,
        "filter": "waiting",
        "scope": "all",
        "days": 7,
    }
    return values.get(field)


def _tool_arguments(tool: str, input_schema: dict | None = None, catalog: ResourceCatalog | None = None) -> dict:
    """Build arguments from the advertised schema, adapting only if it asks for request."""
    catalog = catalog or ResourceCatalog()
    spec = SPEC_BY_NAME[tool]
    schema = input_schema or {}
    properties = _schema_properties(schema)
    fields = set(spec.required_fields) | set(properties)
    fields.discard("request")
    args = {field: _value_for_field(field, catalog) for field in fields}
    args = {field: value for field, value in args.items() if value is not None}
    if "request" in properties and isinstance(properties["request"], dict):
        nested = properties["request"]
        nested_fields = set(nested.get("required", [])) | set(_schema_properties(nested))
        args = {field: _value_for_field(field, catalog) for field in nested_fields}
        args = {field: value for field, value in args.items() if value is not None}
        return {"request": args}
    return args


def _validate_schema(value: object, schema: dict, path: str = "arguments") -> list[str]:
    """Small dependency-free validator for the JSON Schema subset MCP advertises."""
    if not isinstance(schema, dict):
        return []
    errors: list[str] = []
    if schema.get("type") == "object":
        if not isinstance(value, dict):
            return [f"{path}: expected object"]
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}.{key}: required")
        for key, child in _schema_properties(schema).items():
            if key in value:
                errors.extend(_validate_schema(value[key], child, f"{path}.{key}"))
    elif schema.get("type") == "string" and not isinstance(value, str):
        errors.append(f"{path}: expected string")
    elif schema.get("type") == "integer" and (not isinstance(value, int) or isinstance(value, bool)):
        errors.append(f"{path}: expected integer")
    elif schema.get("type") == "boolean" and not isinstance(value, bool):
        errors.append(f"{path}: expected boolean")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value is outside enum")
    return errors


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


def _contains_sensitive(value: object) -> bool:
    text = json.dumps(value, sort_keys=True, default=str).lower()
    return any(marker in text for marker in SENSITIVE_MARKERS)


def _classify_call(response: httpx.Response, payload: dict, expected_id: int, operation: str, expected_workspace: str | None, *, expect_denial: bool = False) -> tuple[str, str | None]:
    if response.status_code < 200 or response.status_code >= 300:
        return "FAIL_PROTOCOL", f"HTTP status {response.status_code}"
    if payload.get("jsonrpc") != "2.0" or payload.get("id") != expected_id:
        return "FAIL_PROTOCOL", "invalid JSON-RPC response id or version"
    if isinstance(payload.get("error"), dict):
        return "FAIL_PROTOCOL", "JSON-RPC protocol error"
    result = payload.get("result")
    if not isinstance(result, dict):
        return "FAIL_PROTOCOL", "missing MCP result"
    if result.get("isError") is True:
        return ("PASS_EXPECTED_DENIAL", "MCP result isError=true") if expect_denial else ("FAIL_UNEXPECTED_DENIAL", "MCP result isError=true")
    structured = result.get("structuredContent")
    if not isinstance(structured, dict):
        return "FAIL_SCHEMA", "structuredContent is required"
    status = structured.get("status")
    if status in DENIAL_STATUSES:
        return ("PASS_EXPECTED_DENIAL", f"structured status={status}") if expect_denial else ("FAIL_UNEXPECTED_DENIAL", f"structured status={status}")
    if status not in POSITIVE_STATUSES:
        return "FAIL_SCHEMA", "structuredContent.status is not available"
    data = structured.get("data")
    if not isinstance(data, dict):
        return "FAIL_SCHEMA", "structuredContent.data is required"
    required = CONTRACT_OPERATIONS.get(operation, {}).get("required", ())
    missing = [field for field in required if field not in data]
    if missing:
        return "FAIL_SCHEMA", f"missing operation fields: {', '.join(missing)}"
    if expected_workspace and data.get("workspace_id") != expected_workspace:
        return "FAIL_SCHEMA", "response workspace differs from discovered workspace"
    if _contains_sensitive(payload):
        return "FAIL_SCHEMA", "response contains sensitive token material"
    return "PASS_POSITIVE", None


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
        "source": {"render_base": "codex/mcp-e2e-runner-firebase-fix", "aws_revision": "3aca5d1"},
        "contract": {"expected_operations": len(EXPECTED_OPERATIONS), "expected_tools": len(expected_tools)},
        "prerequisites": {},
        "tool_results": [],
        "status": "BLOCKED",
        "classification_summary": {},
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
            report["mcp_initialize"] = {"http_status": init_response.status_code, "jsonrpc_error": bool(init_payload.get("error")), "valid": init_payload.get("jsonrpc") == "2.0" and init_payload.get("id") == 1}
            if not report["mcp_initialize"]["valid"]:
                _mark_blocked(report, "MCP initialize did not return a valid JSON-RPC response.")
                return report
            rpc("notifications/initialized", None)
            list_response, list_payload = rpc("tools/list", 2, {})
            advertised_items = [item for item in list_payload.get("result", {}).get("tools", []) if isinstance(item, dict)]
            advertised = {item.get("name") for item in advertised_items}
            schemas = {item["name"]: item.get("inputSchema", {}) for item in advertised_items if isinstance(item.get("name"), str)}
            report["tools_list"] = {"http_status": list_response.status_code, "advertised_private_tools": len(advertised & set(expected_tools)), "missing_private_tools": sorted(set(expected_tools) - advertised), "schemas_available": len(schemas)}
            if list_response.status_code >= 400 or not advertised:
                _mark_blocked(report, "MCP tools/list did not return a usable private-tool catalog.")
                return report
            catalog = ResourceCatalog()
            report["resource_discovery"] = {"status": "RUNNING", "discovered": {}}

            def call_tool(tool: str, request_id: int, catalog_for_call: ResourceCatalog) -> tuple[httpx.Response, dict, dict]:
                schema = schemas.get(tool, {})
                arguments = _tool_arguments(tool, schema, catalog_for_call)
                schema_errors = _validate_schema(arguments, schema)
                if schema_errors:
                    return httpx.Response(599), {"jsonrpc": "2.0", "id": request_id, "error": {"code": "invalid_runner_arguments"}}, {"schema_errors": schema_errors, "arguments": arguments}
                response, payload = rpc("tools/call", request_id, {"name": tool, "arguments": arguments})
                return response, payload, {"arguments": arguments}

            discovery_specs = ["neyvro_search_companies", "neyvro_list_opportunities", "neyvro_list_conversations", "neyvro_search_buyers"]
            for index, discovery_tool in enumerate(discovery_specs, start=100):
                if discovery_tool not in advertised:
                    continue
                response, payload, metadata = call_tool(discovery_tool, index, catalog)
                if response.status_code < 400 and not payload.get("error"):
                    catalog = _catalog_from_result(payload, catalog)
                report["resource_discovery"][discovery_tool] = {"http_status": response.status_code, "schema_errors": metadata.get("schema_errors", [])}
            report["resource_discovery"]["discovered"] = {key: value for key, value in vars(catalog).items() if value}
            missing = [field for field in ("workspace_id", "company_id", "opportunity_id", "conversation_id") if not getattr(catalog, field)]
            if missing:
                report["resource_discovery"]["status"] = "BLOCKED_MISSING_FIXTURE"
                _mark_blocked(report, f"Authorized synthetic fixture discovery did not return: {', '.join(missing)}")
                return report
            report["resource_discovery"]["status"] = "PASS"
            for tool in expected_tools:
                request_id = 1000 + len(report["tool_results"])
                response, payload, metadata = call_tool(tool, request_id, catalog)
                classification, detail = _classify_call(response, payload, request_id, TOOL_OPERATION_MAP[tool], catalog.workspace_id)
                if metadata.get("schema_errors"):
                    classification, detail = "FAIL_SCHEMA", "; ".join(metadata["schema_errors"])
                result = CallResult(tool, TOOL_OPERATION_MAP[tool], classification, response.status_code, _error_code(payload), classification, detail)
                report["tool_results"].append(result.__dict__)
    except httpx.HTTPError as exc:
        _mark_blocked(report, f"Local MCP HTTP failure: {type(exc).__name__}")
        return report
    report["classification_summary"] = {status: sum(item["status"] == status for item in report["tool_results"]) for status in {item["status"] for item in report["tool_results"]}}
    report["status"] = "PASS" if report["tool_results"] and all(item["status"] == "PASS_POSITIVE" for item in report["tool_results"]) else "FAIL"
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
    parser.add_argument("--gateway", default="http://127.0.0.1:8010")
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
