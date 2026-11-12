import base64
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.firebase_test_token import FirebaseTokenError, _decode_claims_without_trust, acquire_token


def _token(claims):
    encoded = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")
    return f"header.{encoded}.signature"


def test_firebase_token_claim_decoder_is_not_a_signature_verifier():
    assert _decode_claims_without_trust(_token({"sub": "uid"})) == {"sub": "uid"}


def test_firebase_token_flow_rejects_non_test_project():
    with pytest.raises(FirebaseTokenError, match="dedicated neyvro-mcp-test"):
        acquire_token(api_key="key", email="a@example.test", password="password", project_id="production")


def test_firebase_token_flow_requires_verified_email(monkeypatch):
    class Response:
        status_code = 200

        def json(self):
            return {"idToken": _token({"iss": "https://securetoken.google.com/neyvro-mcp-test", "aud": "neyvro-mcp-test", "sub": "uid", "auth_time": 2_000_000_000, "exp": 2_000_000_100, "email_verified": False}), "localId": "uid", "expiresIn": "3600"}

    monkeypatch.setattr("scripts.firebase_test_token.httpx.post", lambda *args, **kwargs: Response())
    with pytest.raises(FirebaseTokenError, match="email must be verified"):
        acquire_token(api_key="key", email="a@example.test", password="password")
