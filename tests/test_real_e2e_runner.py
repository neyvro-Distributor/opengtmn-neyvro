from argparse import Namespace
import httpx
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.run_mcp_real_e2e import (
    EXPECTED_OPERATIONS,
    ENABLED_PRIVATE_TOOLS,
    ResourceCatalog,
    SPEC_BY_NAME,
    _classify_call,
    _catalog_from_result,
    _tool_arguments,
    _validate_schema,
    run,
)


def test_real_runner_refuses_non_loopback_targets():
    report = run(Namespace(gateway="https://example.invalid", backend="http://127.0.0.1:8001", token_env="NEYVRO_E2E_TOKEN_A", timeout=0.1))
    assert report["status"] == "BLOCKED"
    assert len(report["tool_results"]) == 30
    assert all(item["status"] == "BLOCKED" for item in report["tool_results"])


def test_real_runner_reports_unavailable_local_stack_without_secrets(monkeypatch):
    monkeypatch.delenv("NEYVRO_E2E_TOKEN_A", raising=False)
    report = run(Namespace(gateway="http://127.0.0.1:8010", backend="http://127.0.0.1:8001", token_env="NEYVRO_E2E_TOKEN_A", timeout=0.1))
    assert report["status"] == "BLOCKED"
    assert len(EXPECTED_OPERATIONS) == 14
    assert report["contract"]["expected_tools"] == 30
    assert "Bearer" not in str(report)


def test_all_private_tool_arguments_use_discovered_lowercase_resource_ids():
    catalog = ResourceCatalog(
        workspace_id="00000000-0000-0000-0000-000000000001",
        company_id="00000000-0000-0000-0000-000000000002",
        buyer_id="00000000-0000-0000-0000-000000000003",
        opportunity_id="00000000-0000-0000-0000-000000000004",
        conversation_id="00000000-0000-0000-0000-000000000005",
    )
    for tool in sorted(ENABLED_PRIVATE_TOOLS):
        arguments = _tool_arguments(tool, {}, catalog)
        for field in SPEC_BY_NAME[tool].required_fields:
            assert field in arguments or ("request" in arguments and field in arguments["request"])


def test_tool_request_wrapper_is_adaptive_and_schema_valid():
    catalog = ResourceCatalog(company_id="00000000-0000-0000-0000-000000000002")
    schema = {
        "type": "object",
        "required": ["request"],
        "properties": {"request": {"type": "object", "required": ["company_id"], "properties": {"company_id": {"type": "string"}}}},
    }
    arguments = _tool_arguments("neyvro_get_company_twin", schema, catalog)
    assert arguments == {"request": {"company_id": "00000000-0000-0000-0000-000000000002"}}
    assert _validate_schema(arguments, schema) == []


def test_resource_discovery_extracts_only_lowercase_uuid_fixture_ids():
    catalog = _catalog_from_result({"result": {"structuredContent": {"status": "available", "data": {
        "workspace_id": "00000000-0000-0000-0000-000000000001",
        "companies": [{"company_id": "00000000-0000-0000-0000-000000000002"}],
        "opportunities": [{"opportunity_id": "00000000-0000-0000-0000-000000000004"}],
        "conversations": [{"conversation_id": "00000000-0000-0000-0000-000000000005"}],
        "buyers": [{"buyer_id": "00000000-0000-0000-0000-000000000003"}],
    }}}}, ResourceCatalog())
    assert catalog.company_id == "00000000-0000-0000-0000-000000000002"
    assert catalog.buyer_id == "00000000-0000-0000-0000-000000000003"
    assert catalog.opportunity_id == "00000000-0000-0000-0000-000000000004"
    assert catalog.conversation_id == "00000000-0000-0000-0000-000000000005"


def test_classifier_rejects_http_200_is_error_and_structured_denials():
    response = httpx.Response(200)
    base = {"jsonrpc": "2.0", "id": 7, "result": {"isError": True}}
    assert _classify_call(response, base, 7, "companies.search", None)[0] == "FAIL_UNEXPECTED_DENIAL"
    denial = {"jsonrpc": "2.0", "id": 7, "result": {"structuredContent": {"status": "forbidden"}}}
    assert _classify_call(response, denial, 7, "companies.search", None)[0] == "FAIL_UNEXPECTED_DENIAL"
    assert _classify_call(response, denial, 7, "companies.search", None, expect_denial=True)[0] == "PASS_EXPECTED_DENIAL"


def test_classifier_requires_contract_data_and_workspace():
    response = httpx.Response(200)
    payload = {"jsonrpc": "2.0", "id": 7, "result": {"structuredContent": {"status": "available", "data": {"workspace_id": "w"}}}}
    classification, detail = _classify_call(response, payload, 7, "companies.search", "w")
    assert classification == "FAIL_SCHEMA"
    assert detail and "missing operation fields" in detail
