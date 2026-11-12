#!/usr/bin/env python3
"""Acquire a Firebase test ID token without printing or persisting secrets.

This helper is intentionally limited to the dedicated nonproduction project.
It can be used as a library by a local E2E launcher; the CLI reports metadata
only and never emits the ID token, password, refresh token, or API key.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import time
from typing import Any

import httpx

TEST_PROJECT_ID = "neyvro-mcp-test"
IDENTITY_TOOLKIT_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"


class FirebaseTokenError(RuntimeError):
    pass


def _decode_claims_without_trust(token: str) -> dict[str, Any]:
    """Decode claims for routing checks only; signature trust belongs to gateway Admin SDK."""
    try:
        segment = token.split(".")[1]
        segment += "=" * (-len(segment) % 4)
        claims = json.loads(base64.urlsafe_b64decode(segment).decode("utf-8"))
    except (IndexError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FirebaseTokenError("Firebase returned a malformed ID token") from exc
    if not isinstance(claims, dict):
        raise FirebaseTokenError("Firebase ID token claims are not an object")
    return claims


def acquire_token(*, api_key: str, email: str, password: str, project_id: str = TEST_PROJECT_ID, timeout: float = 15.0) -> tuple[str, dict[str, Any]]:
    """Return a real Firebase ID token and safe metadata; never log inputs."""
    if project_id != TEST_PROJECT_ID:
        raise FirebaseTokenError("only the dedicated neyvro-mcp-test project is permitted")
    if not api_key or not email or not password:
        raise FirebaseTokenError("Firebase API key, email, and password are required via environment")
    try:
        response = httpx.post(
            f"{IDENTITY_TOOLKIT_URL}?key={api_key}",
            json={"email": email, "password": password, "returnSecureToken": True},
            timeout=timeout,
            follow_redirects=False,
        )
    except httpx.HTTPError as exc:
        raise FirebaseTokenError(f"Firebase authentication transport failed: {type(exc).__name__}") from exc
    if response.status_code != 200:
        raise FirebaseTokenError("Firebase authentication was rejected")
    try:
        body = response.json()
        token = body["idToken"]
        local_id = body["localId"]
        expires_in = int(body["expiresIn"])
    except (ValueError, KeyError, TypeError) as exc:
        raise FirebaseTokenError("Firebase authentication response was malformed") from exc
    if not isinstance(token, str) or not token or not isinstance(local_id, str) or not local_id:
        raise FirebaseTokenError("Firebase authentication response omitted identity data")
    claims = _decode_claims_without_trust(token)
    expected_issuer = f"https://securetoken.google.com/{project_id}"
    if claims.get("iss") != expected_issuer or claims.get("aud") != project_id:
        raise FirebaseTokenError("Firebase token project or issuer does not match the test project")
    if not isinstance(claims.get("auth_time"), int) or not isinstance(claims.get("exp"), int) or claims["exp"] <= int(time.time()):
        raise FirebaseTokenError("Firebase token has invalid authentication timing")
    if claims.get("sub") != local_id:
        raise FirebaseTokenError("Firebase token subject does not match the authenticated user")
    if claims.get("email_verified") is not True:
        raise FirebaseTokenError("Firebase test user email must be verified")
    return token, {"project_id": project_id, "uid": local_id, "email_verified": True, "expires_in": expires_in}


def main() -> int:
    parser = argparse.ArgumentParser(description="Acquire a Firebase test Token A without printing it")
    parser.add_argument("--timeout", type=float, default=15.0)
    args = parser.parse_args()
    try:
        _, metadata = acquire_token(
            api_key=os.getenv("FIREBASE_WEB_API_KEY", ""),
            email=os.getenv("NEYVRO_FIREBASE_TEST_EMAIL", ""),
            password=os.getenv("NEYVRO_FIREBASE_TEST_PASSWORD", ""),
            project_id=os.getenv("FIREBASE_WEB_PROJECT_ID", TEST_PROJECT_ID),
            timeout=args.timeout,
        )
    except FirebaseTokenError as exc:
        print(f"FIREBASE_TOKEN_A=BLOCKED ({exc})")
        return 2
    print(json.dumps({"status": "READY", "identity": metadata}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
