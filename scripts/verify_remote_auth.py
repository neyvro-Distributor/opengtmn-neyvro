#!/usr/bin/env python3
"""Safely verify one real Neyvro MCP bearer token.

The token is accepted from a hidden prompt or stdin and is never printed,
written to disk, or included in an exception. It is sent only to the
configured MCP endpoint; the verifier fetches public keys from the configured
JWKS endpoint without sending the bearer token there.
"""

from __future__ import annotations

import argparse
import asyncio
import getpass
import json
import os
import sys
from pathlib import Path
from typing import Any

import httpx
import jwt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from neyvro.remote_mcp import JWTVerifier, NeyvroAccessToken, _https_url  # noqa: E402


PROTOCOL_VERSION = "2025-06-18"


def _read_token(args: argparse.Namespace) -> str:
    if args.token_env:
        token = os.environ.get(args.token_env, "")
    elif sys.stdin.isatty():
        token = getpass.getpass("Firebase/MCP access token (input hidden): ")
    else:
        token = sys.stdin.read()
    token = token.strip()
    if not token:
        raise ValueError("no access token supplied")
    if len(token) > 16_384:
        raise ValueError("access token exceeds the verifier limit")
    return token


def _unverified_claim_summary(token: str) -> dict[str, Any]:
    """Classify only; never use these claims for authorization decisions."""
    try:
        header = jwt.get_unverified_header(token)
        claims = jwt.decode(token, options={"verify_signature": False})
    except jwt.PyJWTError:
        return {"parseable": False, "algorithm": None, "issuer_present": False, "audience_present": False}
    return {
        "parseable": True,
        "algorithm": header.get("alg"),
        "issuer_present": isinstance(claims.get("iss"), str),
        "audience_present": bool(claims.get("aud")),
        "firebase_shape": isinstance(claims.get("iss"), str) and claims["iss"].startswith("https://securetoken.google.com/"),
        "mcp_resource_audience_shape": isinstance(claims.get("aud"), str) and claims["aud"].startswith("https://"),
    }


async def _request_status(endpoint: str, token: str | None = None) -> tuple[int, str, bool]:
    headers = {"Accept": "application/json, text/event-stream"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    async with httpx.AsyncClient(timeout=20, follow_redirects=False) as client:
        response = await client.get(endpoint, headers=headers)
    challenge = response.headers.get("www-authenticate", "")
    return response.status_code, challenge, "oauth-protected-resource" in challenge


async def _initialize(endpoint: str, token: str) -> tuple[int, str]:
    headers = {
        "Accept": "application/json, text/event-stream",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "MCP-Protocol-Version": PROTOCOL_VERSION,
    }
    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "neyvro-auth-verifier", "version": "1.0"},
        },
    }
    async with httpx.AsyncClient(timeout=20, follow_redirects=False) as client:
        response = await client.post(endpoint, headers=headers, json=body)
    return response.status_code, response.headers.get("content-type", "")


async def _run(args: argparse.Namespace) -> int:
    required = ("NEYVRO_MCP_OAUTH_ISSUER", "NEYVRO_MCP_OAUTH_AUDIENCE", "NEYVRO_MCP_OAUTH_JWKS_URL", "NEYVRO_MCP_RESOURCE_URL")
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        print("CONFIGURATION_ERROR: missing required OAuth environment settings: " + ", ".join(missing), file=sys.stderr)
        return 2

    issuer = _https_url(os.environ["NEYVRO_MCP_OAUTH_ISSUER"], "NEYVRO_MCP_OAUTH_ISSUER")
    jwks_url = _https_url(os.environ["NEYVRO_MCP_OAUTH_JWKS_URL"], "NEYVRO_MCP_OAUTH_JWKS_URL")
    resource_url = _https_url(os.environ["NEYVRO_MCP_RESOURCE_URL"], "NEYVRO_MCP_RESOURCE_URL")
    endpoint = _https_url(args.endpoint, "--endpoint")
    if not issuer or not jwks_url or not resource_url:
        print("CONFIGURATION_ERROR: OAuth URLs must be valid HTTPS URLs", file=sys.stderr)
        return 2

    token = _read_token(args)
    summary = _unverified_claim_summary(token)
    print(json.dumps({"token_format": summary}, sort_keys=True))
    print("NOTICE: token_format is untrusted classification; authorization uses only verified claims.")

    verifier = JWTVerifier(issuer, os.environ["NEYVRO_MCP_OAUTH_AUDIENCE"], jwks_url, resource_url)
    verified = await verifier.verify_token(token)
    if not isinstance(verified, NeyvroAccessToken):
        print("TOKEN_VERIFICATION=FAILED")
        return 1

    firebase_compatible = summary.get("firebase_shape", False) and not summary.get("mcp_resource_audience_shape", False)
    print("TOKEN_VERIFICATION=PASSED")
    print(f"TOKEN_KIND={'FIREBASE_ID_TOKEN_COMPATIBILITY_MODE' if firebase_compatible else 'MCP_OAUTH_SHAPE_REQUIRES_PROVIDER_CONFIRMATION'}")
    print(f"WORKSPACE_CLAIM_PRESENT={verified.tenant_id is not None}")
    print(f"INTELLIGENCE_READ_SCOPE={'intelligence:read' in verified.scopes}")
    print(f"PROPOSALS_WRITE_SCOPE={'proposals:write' in verified.scopes}")
    print("SUBJECT_VERIFIED=True")
    print("AWS_BACKEND_AUTHORIZED=False")

    anonymous_status, challenge, challenge_has_metadata = await _request_status(endpoint)
    print(f"ANONYMOUS_MCP_STATUS={anonymous_status}")
    print(f"AUTH_CHALLENGE_HAS_RESOURCE_METADATA={challenge_has_metadata}")
    if anonymous_status != 401 or not challenge_has_metadata:
        print("MCP_CHALLENGE=FAILED")
        return 1
    print("MCP_CHALLENGE=PASSED")

    initialize_status, content_type = await _initialize(endpoint, token)
    print(f"AUTHENTICATED_INITIALIZE_STATUS={initialize_status}")
    print(f"AUTHENTICATED_INITIALIZE_CONTENT_TYPE={content_type.split(';', 1)[0]}")
    handshake_ok = 200 <= initialize_status < 300
    print(f"MCP_AUTHENTICATED_HANDSHAKE={'PASSED' if handshake_ok else 'FAILED'}")
    if not handshake_ok:
        return 1

    if verified.tenant_id is None:
        print("PRIVATE_TENANT_AUTHORIZATION=BLOCKED_NO_TRUSTED_WORKSPACE_CLAIM")
        return 2
    print("PRIVATE_TENANT_AUTHORIZATION=IDENTITY_CLAIM_PRESENT_BACKEND_BRIDGE_STILL_REQUIRED")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint", default=os.getenv("NEYVRO_MCP_ENDPOINT"), required=not os.getenv("NEYVRO_MCP_ENDPOINT"), help="MCP Streamable HTTP endpoint")
    parser.add_argument("--token-env", metavar="NAME", help="Read the token from this environment variable; never use a command-line token argument")
    try:
        return asyncio.run(_run(parser.parse_args()))
    except ValueError as exc:
        message = "no access token supplied" if str(exc) == "no access token supplied" else "invalid verifier configuration or input"
        print(f"VERIFICATION_ERROR: {message}", file=sys.stderr)
        return 2
    except (httpx.HTTPError, OSError) as exc:
        print(f"VERIFICATION_ERROR: {type(exc).__name__}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
