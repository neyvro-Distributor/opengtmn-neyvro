import asyncio

import pytest
from mcp.server.auth.provider import AccessToken

from neyvro import remote_mcp


def test_tool_catalog_is_unique_and_complete():
    names = {spec.name for spec in remote_mcp.TOOL_SPECS}
    assert len(names) == 56
    assert len(names) == len(remote_mcp.TOOL_SPECS)
    assert "neyvro_search_companies" in names
    assert "neyvro_propose_social_post" in names
    assert "neyvro_get_monitoring_status" in names
    assert "neyvro_get_opportunity_history" in names
    assert "neyvro_get_buying_window" in names
    assert "neyvro_evaluate_icp_fit" in names
    assert "neyvro_get_contact_verification" in names
    assert "neyvro_list_campaigns" in names
    assert all(spec.scopes for spec in remote_mcp.TOOL_SPECS)


def test_unconfigured_readiness_is_not_verified():
    report = remote_mcp.readiness_report()

    assert report["authentication"] == "BLOCKED"
    assert report["backend_service_adapter"] == "DISABLED"
    assert set(report["tools"].values()) == {"DISABLED"}


def test_anonymous_and_cross_tenant_requests_are_rejected(monkeypatch):
    spec = remote_mcp.SPEC_BY_NAME["neyvro_get_company_twin"]
    request = remote_mcp.ToolRequest(company_id="company-a")
    monkeypatch.setattr(remote_mcp, "get_access_token", lambda: None)
    assert asyncio.run(remote_mcp.handle_tool(spec, request))["status"] == "unauthorized"

    token = AccessToken(token="opaque", client_id="user-a", scopes=["intelligence:read"])
    monkeypatch.setattr(remote_mcp, "get_access_token", lambda: token)
    remote_mcp.AUTH_CLAIMS.set({"tenant_id": "tenant-a"})
    request = remote_mcp.ToolRequest(workspace_id="tenant-b", company_id="company-a")
    assert asyncio.run(remote_mcp.handle_tool(spec, request))["status"] == "forbidden"


def test_missing_scope_and_pending_approval_are_enforced(monkeypatch):
    token = AccessToken(token="opaque", client_id="user-a", scopes=[])
    monkeypatch.setattr(remote_mcp, "get_access_token", lambda: token)
    remote_mcp.AUTH_CLAIMS.set({"tenant_id": "tenant-a"})
    read_spec = remote_mcp.SPEC_BY_NAME["neyvro_get_company_twin"]
    assert asyncio.run(remote_mcp.handle_tool(read_spec, remote_mcp.ToolRequest(company_id="c")))["status"] == "insufficient_scope"

    token = AccessToken(token="opaque", client_id="user-a", scopes=["intelligence:read", "proposals:write"])
    monkeypatch.setattr(remote_mcp, "get_access_token", lambda: token)
    proposal = remote_mcp.SPEC_BY_NAME["neyvro_propose_campaign"]
    result = asyncio.run(remote_mcp.handle_tool(proposal, remote_mcp.ToolRequest(campaign_id="c")))
    assert result["status"] == "pending_approval"


def test_private_website_targets_are_rejected_before_backend(monkeypatch):
    token = AccessToken(token="opaque", client_id="user-a", scopes=["intelligence:read"])
    monkeypatch.setattr(remote_mcp, "get_access_token", lambda: token)
    remote_mcp.AUTH_CLAIMS.set({"tenant_id": "tenant-a"})
    spec = remote_mcp.SPEC_BY_NAME["neyvro_analyze_website"]
    request = remote_mcp.ToolRequest(payload={"url": "http://127.0.0.1:8000/admin"})
    result = asyncio.run(remote_mcp.handle_tool(spec, request))

    assert result["status"] == "invalid_request"
    assert result["error"]["code"] == "invalid_request"


def test_backend_adapter_never_uses_inbound_token(monkeypatch):
    token = AccessToken(token="incoming-secret", client_id="user-a", scopes=["intelligence:read"])
    monkeypatch.setattr(remote_mcp, "get_access_token", lambda: token)
    remote_mcp.AUTH_CLAIMS.set({"tenant_id": "tenant-a"})
    spec = remote_mcp.SPEC_BY_NAME["neyvro_get_company_twin"]
    captured = {}

    async def fake_request(specification, request, tenant):
        captured.update({"tenant": tenant, "token": remote_mcp.BACKEND.service_token})
        return {"status": "available", "data": {"ok": True}}

    monkeypatch.setattr(remote_mcp.BACKEND, "request", fake_request)
    result = asyncio.run(remote_mcp.handle_tool(spec, remote_mcp.ToolRequest(company_id="c")))

    assert result["status"] == "available"
    assert captured["tenant"] == "tenant-a"
    assert captured["token"] != "incoming-secret"


def test_streamable_http_server_registers_official_transport():
    server = remote_mcp.build_server()
    app = server.streamable_http_app()
    assert app is not None
    assert any(route.path == "/mcp" for route in app.routes)
    assert any(route.path == "/health" for route in remote_mcp.REMOTE_APP.routes)


def test_remote_server_exposes_public_skill_resources_and_prompts_without_customer_data():
    server = remote_mcp.build_server()
    assert len(server._resource_manager._resources) == 35
    assert len(server._prompt_manager._prompts) == 35
    assert "neyvro://skills/gtm-strategy" in server._resource_manager._resources
    assert "gtm-strategy" in server._prompt_manager._prompts
