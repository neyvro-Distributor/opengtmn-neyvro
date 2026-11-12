import asyncio
import uuid
import time

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.hazmat.primitives import serialization

from neyvro import remote_mcp as mcp


def test_phase2_has_thirty_enabled_tools_and_fourteen_contract_operations():
    assert len(mcp.ENABLED_PRIVATE_TOOLS) == 30
    assert len(mcp.CONTRACT_OPERATIONS) == 14
    assert set(mcp.OPERATION_ADAPTERS) == set(mcp.CONTRACT_OPERATIONS)
    assert all(name in mcp.SPEC_BY_NAME for name in mcp.ENABLED_PRIVATE_TOOLS)
    assert all(mcp.SPEC_BY_NAME[name].readiness == "AVAILABLE" for name in mcp.ENABLED_PRIVATE_TOOLS)


def test_contract_routes_and_mail_scopes_are_exact():
    assert mcp.SPEC_BY_NAME["neyvro_get_conversation"].required_fields == ("conversation_id",)
    for name in ("neyvro_get_connections", "neyvro_get_capabilities", "neyvro_get_permissions", "neyvro_get_sender_status", "neyvro_get_campaign_metrics"):
        assert mcp.SPEC_BY_NAME[name].scopes == ("mail:read",)
    assert mcp.SPEC_BY_NAME["neyvro_get_followup_queue"].operation == "conversations.list"
    assert mcp.CONTRACT_OPERATIONS["conversations.list"]["path"] == "/v1/mcp/conversations"
    assert mcp.CONTRACT_OPERATIONS["companies.get"]["path"] == "/v1/mcp/companies/{company_id}"


def test_unsupported_tools_are_not_callable():
    unsupported = set(mcp.SPEC_BY_NAME) - mcp.ENABLED_PRIVATE_TOOLS
    assert len(unsupported) == 26
    assert "neyvro_propose_campaign" in unsupported
    assert "neyvro_research_account" in unsupported


def test_gateway_assertions_are_fresh_exact_and_never_use_inbound_token(monkeypatch):
    key = ec.generate_private_key(ec.SECP256R1())
    pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()).decode()
    backend = mcp.BackendClient()
    backend.enabled = True
    backend.base_url = "http://127.0.0.1:9000"
    backend.gateway_private_key = pem
    identity = mcp.NeyvroAccessToken(token="inbound-secret", client_id="firebase-user", firebase_uid="firebase-user", email_verified=True, scopes=["mail:read"], resource="https://mcp.example/mcp")
    spec = mcp.SPEC_BY_NAME["neyvro_get_connections"]
    request = mcp.ToolRequest()
    first = backend._assertion(identity, spec, request)
    second = backend._assertion(identity, spec, request)
    assert first != second
    claims = jwt.decode(first, key.public_key(), algorithms=["ES256"], audience="neyvro-mcp-exchange", issuer="neyvro-mcp-gateway")
    headers = jwt.get_unverified_header(first)
    assert headers == {"alg": "ES256", "typ": "gateway+jwt", "kid": "gw-1"}
    assert claims["sub"] == "firebase-user"
    assert claims["op"] == "mail.overview"
    assert claims["scope"] == "mail:read"
    assert claims["jti"] != jwt.decode(second, options={"verify_signature": False})["jti"]
    assert "inbound-secret" not in first


def test_invalid_contract_inputs_are_rejected():
    with pytest.raises(ValueError):
        mcp.ToolRequest(company_id="not-a-uuid")
    with pytest.raises(ValueError):
        mcp.ToolRequest(workspace_id="NOT-A-UUID")


def test_response_envelope_requires_workspace_and_operation():
    with pytest.raises(Exception):
        mcp.ContractResponse.model_validate({"workspace_id": str(uuid.uuid4())})


def test_buyer_projection_cannot_return_another_person():
    spec = mcp.SPEC_BY_NAME["neyvro_get_buyer"]
    request = mcp.ToolRequest(company_id="00000000-0000-0000-0000-000000000001", buyer_id="00000000-0000-0000-0000-000000000002")
    raw = {"workspace_id": "00000000-0000-0000-0000-000000000003", "people": [{"id": request.buyer_id, "name": "Synthetic Buyer"}, {"id": "other", "name": "Other"}]}
    projected = mcp._project_tool_result(spec, request, {"status": "available", "data": raw})
    assert projected["data"]["person"]["id"] == request.buyer_id
    assert "Other" not in str(projected)


def test_firebase_verifier_requires_parent_signature_and_auth_time():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    verifier = mcp.FirebaseTokenVerifier("test-project", "https://mcp.example/mcp")
    verifier.client.get_signing_key_from_jwt = lambda _token: type("Key", (), {"key": key.public_key()})()
    base = {"iss": "https://securetoken.google.com/test-project", "aud": "test-project", "sub": "uid-1", "iat": int(time.time()), "exp": int(time.time()) + 300, "email_verified": True}
    missing_auth_time = jwt.encode(base, key, algorithm="RS256")
    assert asyncio.run(verifier.verify_token(missing_auth_time)) is None


def test_each_of_the_thirty_enabled_tools_passes_its_gateway_boundary(monkeypatch):
    identity = mcp.NeyvroAccessToken(token="opaque", client_id="uid", firebase_uid="uid", email_verified=True, scopes=["intelligence:read", "mail:read"], resource="https://mcp.example/mcp")
    monkeypatch.setattr(mcp, "get_access_token", lambda: identity)
    calls = []

    async def fake_request(spec, request, token):
        calls.append((spec.name, spec.operation, spec.scopes, request))
        return {"status": "available", "data": {"workspace_id": "00000000-0000-0000-0000-000000000003", "operation": spec.operation, "people": [{"id": request.buyer_id}]}}

    monkeypatch.setattr(mcp.BACKEND, "request", fake_request)
    request = mcp.ToolRequest(workspace_id="00000000-0000-0000-0000-000000000003", company_id="00000000-0000-0000-0000-000000000001", buyer_id="00000000-0000-0000-0000-000000000002", opportunity_id="00000000-0000-0000-0000-000000000004", conversation_id="00000000-0000-0000-0000-000000000005")
    results = {name: asyncio.run(mcp.handle_tool(mcp.SPEC_BY_NAME[name], request)) for name in sorted(mcp.ENABLED_PRIVATE_TOOLS)}
    assert set(results) == mcp.ENABLED_PRIVATE_TOOLS
    assert all(result["status"] == "available" for result in results.values())
    assert len(calls) == 30


def test_firebase_scope_claims_are_ignored_without_an_explicit_test_grant(monkeypatch):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    verifier = mcp.FirebaseTokenVerifier("neyvro-mcp-test", "https://mcp.example/mcp", admin_verifier=lambda token, check_revoked=True: {"sub": "uid-1", "email_verified": True})
    verifier.client.get_signing_key_from_jwt = lambda _token: type("Key", (), {"key": key.public_key()})()
    claims = {"iss": "https://securetoken.google.com/neyvro-mcp-test", "aud": "neyvro-mcp-test", "sub": "uid-1", "iat": int(time.time()), "exp": int(time.time()) + 300, "auth_time": int(time.time()), "email_verified": True, "scope": "mail:read"}
    token = jwt.encode(claims, key, algorithm="RS256")
    verified = asyncio.run(verifier.verify_token(token))
    assert verified is not None
    assert verified.scopes == []
    assert verified.grant_source == "none"
    monkeypatch.setattr(mcp, "get_access_token", lambda: verified)
    result = asyncio.run(mcp.handle_tool(mcp.SPEC_BY_NAME["neyvro_get_connections"], mcp.ToolRequest()))
    assert result["status"] == "insufficient_scope"
    assert result["missing_scopes"] == ["mail:read"]


def test_firebase_uses_only_the_exact_server_managed_test_grant(monkeypatch):
    monkeypatch.setenv("NEYVRO_MCP_FIREBASE_TEST_MODE", "true")
    expires_at = int(time.time()) + 1800
    monkeypatch.setenv("NEYVRO_MCP_FIREBASE_TEST_GRANTS_JSON", f'{{"uid-1":{{"scopes":["mail:read"],"expires_at":{expires_at}}}}}')
    grants = mcp._load_firebase_test_grants("neyvro-mcp-test")
    assert grants["uid-1"].effective() == ("mail:read",)
    assert mcp._load_firebase_test_grants("neyvro-production") == {}


def test_external_oauth_requires_issuer_qualified_identity_binding():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    issuer = "https://issuer.example"
    verifier = mcp.JWTVerifier(issuer, "https://mcp.example", "https://issuer.example/jwks", "https://mcp.example/mcp")
    verifier.client.get_signing_key_from_jwt = lambda _token: type("Key", (), {"key": key.public_key()})()
    claims = {"iss": issuer, "aud": "https://mcp.example", "sub": "oauth-sub", "iat": int(time.time()), "exp": int(time.time()) + 300, "scope": "intelligence:read"}
    token = jwt.encode(claims, key, algorithm="RS256")
    unlinked = asyncio.run(verifier.verify_token(token))
    assert unlinked is not None and unlinked.firebase_uid == ""
    verifier.identity_bindings[f"{issuer}\x00oauth-sub"] = mcp.IdentityBinding(issuer, "oauth-sub", "firebase-uid")
    linked = asyncio.run(verifier.verify_token(token))
    assert linked is not None and linked.firebase_uid == "firebase-uid"


def test_identity_and_mail_scopes_cannot_cross_authorize():
    identity = mcp.NeyvroAccessToken(token="x", client_id="u", firebase_uid="f", scopes=["intelligence:read"], auth_mode="oauth")
    intelligence = mcp.SPEC_BY_NAME["neyvro_search_companies"]
    mail = mcp.SPEC_BY_NAME["neyvro_get_connections"]
    assert mcp._evaluate_scope_grant(identity, intelligence) is None
    assert mcp._evaluate_scope_grant(identity, mail)["missing_scopes"] == ["mail:read"]
    identity.scopes = ["mail:read"]
    assert mcp._evaluate_scope_grant(identity, intelligence)["missing_scopes"] == ["intelligence:read"]


def test_firebase_and_external_oauth_configuration_conflict_fails_closed(monkeypatch):
    monkeypatch.setenv("NEYVRO_MCP_FIREBASE_PROJECT_ID", "neyvro-mcp-test")
    monkeypatch.setenv("NEYVRO_MCP_FIREBASE_SERVICE_ACCOUNT_JSON", "{}")
    monkeypatch.setenv("NEYVRO_MCP_RESOURCE_URL", "https://mcp.example/mcp")
    monkeypatch.setenv("NEYVRO_MCP_OAUTH_ISSUER", "https://issuer.example")
    monkeypatch.setenv("NEYVRO_MCP_OAUTH_AUDIENCE", "mcp-resource")
    monkeypatch.setenv("NEYVRO_MCP_OAUTH_JWKS_URL", "https://issuer.example/jwks")
    mcp.build_server()
    assert mcp.readiness_report()["authentication"] == "BLOCKED"
    assert "cannot be configured together" in mcp.readiness_report()["notes"][0]


def test_token_b_cannot_be_signed_for_an_ungranted_scope():
    key = ec.generate_private_key(ec.SECP256R1())
    pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()).decode()
    backend = mcp.BackendClient()
    backend.enabled = True
    backend.base_url = "http://127.0.0.1:9000"
    backend.gateway_private_key = pem
    identity = mcp.NeyvroAccessToken(token="inbound", client_id="u", firebase_uid="f", scopes=["intelligence:read"], email_verified=True)
    with pytest.raises(mcp.BridgeConfigurationError):
        backend._assertion(identity, mcp.SPEC_BY_NAME["neyvro_get_connections"], mcp.ToolRequest())
