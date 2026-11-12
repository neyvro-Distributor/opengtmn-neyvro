import asyncio
import time

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
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


def test_public_tools_are_separate_from_the_56_backend_specs():
    server = remote_mcp.build_server()
    tools = server._tool_manager._tools
    assert len(remote_mcp.TOOL_SPECS) == 56
    assert "neyvro_list_skills" in tools
    assert "neyvro_get_skill" in tools
    assert set(tools) >= set(remote_mcp.ENABLED_PRIVATE_TOOLS)
    assert tools["neyvro_list_skills"].meta["auth"] == "PUBLIC"
    assert tools["neyvro_get_skill"].meta["read_only"] is True


def test_unconfigured_readiness_is_not_verified():
    report = remote_mcp.readiness_report()

    assert report["authentication"] == "BLOCKED"
    assert report["customer_data_authorization"] == "BLOCKED"
    assert report["backend_service_adapter"] == "DISABLED"
    assert set(report["tools"].values()) == {"DISABLED"}


def test_oauth_configuration_is_configured_not_verified(monkeypatch):
    monkeypatch.setenv("NEYVRO_MCP_OAUTH_ISSUER", "https://issuer.example")
    monkeypatch.setenv("NEYVRO_MCP_OAUTH_AUDIENCE", "neyvro-mcp")
    monkeypatch.setenv("NEYVRO_MCP_OAUTH_JWKS_URL", "https://issuer.example/.well-known/jwks.json")
    monkeypatch.setenv("NEYVRO_MCP_RESOURCE_URL", "https://mcp.example/mcp")
    monkeypatch.setattr(remote_mcp, "_AUTH_VERIFIED", False)
    assert remote_mcp.readiness_report()["authentication"] == "CONFIGURED"


def test_oauth_configuration_preserves_issuer_trailing_slash(monkeypatch):
    monkeypatch.setenv("NEYVRO_MCP_OAUTH_ISSUER", "https://issuer.example/")
    monkeypatch.setenv("NEYVRO_MCP_OAUTH_AUDIENCE", "neyvro-mcp")
    monkeypatch.setenv("NEYVRO_MCP_OAUTH_JWKS_URL", "https://issuer.example/jwks")
    monkeypatch.setenv("NEYVRO_MCP_RESOURCE_URL", "https://mcp.example/mcp")
    issuer, _, _, _, _ = remote_mcp._oauth_config()
    assert issuer == "https://issuer.example/"


def test_jwt_verifier_enforces_signature_issuer_audience_and_tenant(monkeypatch):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    verifier = remote_mcp.JWTVerifier("https://issuer.example", "neyvro-mcp", "https://issuer.example/jwks", "https://mcp.example/mcp")
    verifier.client.get_signing_key_from_jwt = lambda _token: type("Key", (), {"key": private_key.public_key()})()
    claims = {"iss": "https://issuer.example", "aud": "neyvro-mcp", "sub": "user-a", "workspace_id": "tenant-a", "scope": "intelligence:read", "iat": int(time.time()), "exp": int(time.time()) + 300}
    token = jwt.encode(claims, private_key, algorithm="RS256")
    verified = asyncio.run(verifier.verify_token(token))
    assert isinstance(verified, remote_mcp.NeyvroAccessToken)
    assert verified.tenant_id == "tenant-a"
    assert verified.scopes == ["intelligence:read"]

    bad_audience = jwt.encode({**claims, "aud": "wrong-resource"}, private_key, algorithm="RS256")
    assert asyncio.run(verifier.verify_token(bad_audience)) is None


def test_jwt_verifier_rejects_wrong_issuer_expiry_signature_and_malformed_scopes(monkeypatch):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    other_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    verifier = remote_mcp.JWTVerifier("https://issuer.example/", "neyvro-mcp", "https://issuer.example/jwks", "https://mcp.example/mcp")
    verifier.client.get_signing_key_from_jwt = lambda _token: type("Key", (), {"key": private_key.public_key()})()
    base = {"iss": "https://issuer.example/", "aud": "neyvro-mcp", "sub": "user-a", "iat": int(time.time()), "exp": int(time.time()) + 300}

    wrong_issuer = jwt.encode({**base, "iss": "https://other.example"}, private_key, algorithm="RS256")
    expired = jwt.encode({**base, "exp": int(time.time()) - 60}, private_key, algorithm="RS256")
    invalid_signature = jwt.encode(base, other_key, algorithm="RS256")
    malformed_scopes = jwt.encode({**base, "scope": {"not": "a-scope"}}, private_key, algorithm="RS256")

    assert asyncio.run(verifier.verify_token(wrong_issuer)) is None
    assert asyncio.run(verifier.verify_token(expired)) is None
    assert asyncio.run(verifier.verify_token(invalid_signature)) is None
    assert asyncio.run(verifier.verify_token(malformed_scopes)) is None


def test_jwt_verifier_rejects_missing_or_blank_subject():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    verifier = remote_mcp.JWTVerifier("https://issuer.example", "neyvro-mcp", "https://issuer.example/jwks", "https://mcp.example/mcp")
    verifier.client.get_signing_key_from_jwt = lambda _token: type("Key", (), {"key": private_key.public_key()})()
    base = {"iss": "https://issuer.example", "aud": "neyvro-mcp", "iat": int(time.time()), "exp": int(time.time()) + 300, "scope": "intelligence:read"}

    for subject in (None, "", "   "):
        claims = {**base, "sub": subject} if subject is not None else base
        token = jwt.encode(claims, private_key, algorithm="RS256")
        assert asyncio.run(verifier.verify_token(token)) is None


def test_missing_workspace_is_verified_but_not_private_authorization():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    verifier = remote_mcp.JWTVerifier("https://issuer.example", "neyvro-mcp", "https://issuer.example/jwks", "https://mcp.example/mcp")
    verifier.client.get_signing_key_from_jwt = lambda _token: type("Key", (), {"key": private_key.public_key()})()
    token = jwt.encode({"iss": "https://issuer.example", "aud": "neyvro-mcp", "sub": "user-a", "iat": int(time.time()), "exp": int(time.time()) + 300, "scope": "intelligence:read"}, private_key, algorithm="RS256")
    verified = asyncio.run(verifier.verify_token(token))
    assert isinstance(verified, remote_mcp.NeyvroAccessToken)
    assert verified.tenant_id is None

    read_spec = remote_mcp.SPEC_BY_NAME["neyvro_get_company_twin"]
    remote_mcp_get_access_token = remote_mcp.get_access_token
    try:
        remote_mcp.get_access_token = lambda: verified
        result = asyncio.run(remote_mcp.handle_tool(read_spec, remote_mcp.ToolRequest(company_id="00000000-0000-0000-0000-000000000003")))
    finally:
        remote_mcp.get_access_token = remote_mcp_get_access_token
    assert result["status"] == "disabled"


def test_jwks_rotation_uses_the_current_signing_key():
    first_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    second_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    verifier = remote_mcp.JWTVerifier("https://issuer.example", "neyvro-mcp", "https://issuer.example/jwks", "https://mcp.example/mcp")
    keys = iter((first_key.public_key(), second_key.public_key()))
    verifier.client.get_signing_key_from_jwt = lambda _token: type("Key", (), {"key": next(keys)})()
    claims = {"iss": "https://issuer.example", "aud": "neyvro-mcp", "sub": "user-a", "workspace_id": "tenant-a", "iat": int(time.time()), "exp": int(time.time()) + 300, "scope": "intelligence:read"}
    first = jwt.encode(claims, first_key, algorithm="RS256")
    second = jwt.encode(claims, second_key, algorithm="RS256")
    assert asyncio.run(verifier.verify_token(first)) is not None
    assert asyncio.run(verifier.verify_token(second)) is not None


def test_configured_server_publishes_protected_resource_metadata(monkeypatch):
    monkeypatch.setenv("NEYVRO_MCP_OAUTH_ISSUER", "https://issuer.example")
    monkeypatch.setenv("NEYVRO_MCP_OAUTH_AUDIENCE", "neyvro-mcp")
    monkeypatch.setenv("NEYVRO_MCP_OAUTH_JWKS_URL", "https://issuer.example/.well-known/jwks.json")
    monkeypatch.setenv("NEYVRO_MCP_RESOURCE_URL", "https://mcp.example/mcp")
    app = remote_mcp.build_server().streamable_http_app()
    assert any("oauth-protected-resource" in getattr(route, "path", "") for route in app.routes)


def test_anonymous_and_cross_tenant_requests_are_rejected(monkeypatch):
    spec = remote_mcp.SPEC_BY_NAME["neyvro_get_company_twin"]
    request = remote_mcp.ToolRequest(company_id="00000000-0000-0000-0000-000000000003")
    monkeypatch.setattr(remote_mcp, "get_access_token", lambda: None)
    assert asyncio.run(remote_mcp.handle_tool(spec, request))["status"] == "unauthorized"

    token = remote_mcp.NeyvroAccessToken(token="opaque", client_id="user-a", scopes=["intelligence:read"], resource="https://mcp.example/mcp", tenant_id="tenant-a")
    monkeypatch.setattr(remote_mcp, "get_access_token", lambda: token)
    request = remote_mcp.ToolRequest(workspace_id="00000000-0000-0000-0000-000000000002", company_id="00000000-0000-0000-0000-000000000003")
    assert asyncio.run(remote_mcp.handle_tool(spec, request))["status"] == "disabled"


def test_public_skill_tools_are_anonymous_allowlisted_and_read_only(monkeypatch):
    monkeypatch.setattr(remote_mcp, "get_access_token", lambda: None)
    original = (remote_mcp.SKILLS_ROOT / "ideal-customer-profile/SKILL.md").read_text(encoding="utf-8")

    listed = remote_mcp._public_list_skills(limit=100)
    assert len(listed) == 35
    assert all("path" not in item for item in listed)

    fetched = remote_mcp._public_get_skill("ideal-customer-profile")
    assert fetched["name"] == "ideal-customer-profile"
    assert fetched["content"] == original
    assert (remote_mcp.SKILLS_ROOT / "ideal-customer-profile/SKILL.md").read_text(encoding="utf-8") == original

    with pytest.raises(ValueError, match="unknown public skill"):
        remote_mcp._public_get_skill("../ideal-customer-profile")


def test_public_skill_rate_limit_is_fail_closed(monkeypatch):
    monkeypatch.setattr(remote_mcp, "PUBLIC_LIMITER", remote_mcp.RateLimiter(per_minute=1))
    assert remote_mcp._public_get_skill("ideal-customer-profile")["name"] == "ideal-customer-profile"
    limited = remote_mcp._public_get_skill("ideal-customer-profile")
    assert limited["status"] == "rate_limited"


def test_missing_scope_and_pending_approval_are_enforced(monkeypatch):
    token = remote_mcp.NeyvroAccessToken(token="opaque", client_id="user-a", scopes=[], resource="https://mcp.example/mcp", tenant_id="tenant-a")
    monkeypatch.setattr(remote_mcp, "get_access_token", lambda: token)
    read_spec = remote_mcp.SPEC_BY_NAME["neyvro_get_company_twin"]
    assert asyncio.run(remote_mcp.handle_tool(read_spec, remote_mcp.ToolRequest(company_id="00000000-0000-0000-0000-000000000003"))) ["status"] == "insufficient_scope"

    token = remote_mcp.NeyvroAccessToken(token="opaque", client_id="user-a", scopes=["intelligence:read", "proposals:write"], resource="https://mcp.example/mcp", tenant_id="tenant-a")
    monkeypatch.setattr(remote_mcp, "get_access_token", lambda: token)
    proposal = remote_mcp.SPEC_BY_NAME["neyvro_propose_campaign"]
    result = asyncio.run(remote_mcp.handle_tool(proposal, remote_mcp.ToolRequest(campaign_id="c")))
    assert result["status"] == "disabled"


def test_private_website_targets_are_rejected_before_backend(monkeypatch):
    token = remote_mcp.NeyvroAccessToken(token="opaque", client_id="user-a", scopes=["intelligence:read"], resource="https://mcp.example/mcp", tenant_id="tenant-a")
    monkeypatch.setattr(remote_mcp, "get_access_token", lambda: token)
    spec = remote_mcp.SPEC_BY_NAME["neyvro_analyze_website"]
    request = remote_mcp.ToolRequest(payload={"url": "http://127.0.0.1:8000/admin"})
    result = asyncio.run(remote_mcp.handle_tool(spec, request))

    assert result["status"] == "disabled"


def test_backend_adapter_never_uses_inbound_token(monkeypatch):
    token = remote_mcp.NeyvroAccessToken(token="incoming-secret", client_id="user-a", scopes=["intelligence:read"], resource="https://mcp.example/mcp", tenant_id="tenant-a")
    monkeypatch.setattr(remote_mcp, "get_access_token", lambda: token)
    spec = remote_mcp.SPEC_BY_NAME["neyvro_get_company_twin"]
    captured = {}

    async def fake_request(specification, request, tenant):
        captured.update({"tenant": tenant, "token": tenant.token})
        return {"status": "available", "data": {"ok": True}}

    monkeypatch.setattr(remote_mcp.BACKEND, "request", fake_request)
    result = asyncio.run(remote_mcp.handle_tool(spec, remote_mcp.ToolRequest(company_id="00000000-0000-0000-0000-000000000003")))

    assert result["status"] == "available"
    assert captured["tenant"].tenant_id == "tenant-a"
    assert captured["token"] == "incoming-secret"


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
