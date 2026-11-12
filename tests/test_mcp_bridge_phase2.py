import asyncio
import uuid

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
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
