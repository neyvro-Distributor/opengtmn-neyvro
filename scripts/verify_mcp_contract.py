#!/usr/bin/env python3
"""Compare the Render adapter manifest with the published AWS OpenAPI contract."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from neyvro.remote_mcp import CONTRACT_OPERATIONS  # noqa: E402


def main(path: str) -> int:
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    actual: dict[str, tuple[str, str, str, bool, bool, set[str], set[str]]] = {}
    for route, methods in document.get("paths", {}).items():
        for method, operation in methods.items():
            name = operation.get("x-mcp-operation")
            if not name:
                continue
            parameters = {item["name"] for item in operation.get("parameters", []) if item.get("in") in {"query", "path"}}
            responses = set(operation.get("responses", {}))
            response = operation.get("responses", {}).get("200", {}).get("content", {}).get("application/json", {}).get("schema", {})
            actual[name] = (route, method.upper(), operation.get("x-mcp-scope", ""), operation.get("x-mcp-read-only") is True, operation.get("x-mcp-spends-credits") is True, parameters, responses | {response.get("$ref", "")})

    expected_names = set(CONTRACT_OPERATIONS)
    if set(actual) != expected_names:
        print(f"operation set mismatch: expected={sorted(expected_names)} actual={sorted(actual)}")
        return 1
    errors = []
    for name, contract in CONTRACT_OPERATIONS.items():
        route, method, scope, read_only, spends, params, responses = actual[name]
        path_params = {part[1:-1] for part in contract["path"].split("/") if part.startswith("{") and part.endswith("}")}
        expected_params = set(contract["params"]) | path_params
        if (route, method, scope, read_only, spends, params) != (contract["path"], "GET", contract["scope"], True, False, expected_params):
            errors.append(f"{name}: route/method/scope/flags/params mismatch")
        if "200" not in responses:
            errors.append(f"{name}: missing 200 response")
        required_errors = {"401", "403", "404", "409", "429", "500", "503"}
        if not required_errors <= responses:
            errors.append(f"{name}: missing required error responses")
    if errors:
        print("\n".join(errors))
        return 1
    print(f"PASS: {len(actual)} AWS MCP operations match OpenAPI")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_mcp_contract.py PATH_TO_OPENAPI_JSON")
    raise SystemExit(main(sys.argv[1]))
