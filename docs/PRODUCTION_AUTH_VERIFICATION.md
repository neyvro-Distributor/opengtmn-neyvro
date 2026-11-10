# Production MCP authentication verification

This workflow verifies one real bearer token without printing or storing it.
It does not deploy, enable the AWS adapter, or create tokens.

## 1. Load configuration without committing secrets

Use the local ignored `.env` or an equivalent secure environment source:

```bash
set -a
. ./.env
set +a
export NEYVRO_MCP_ENDPOINT=https://opengtmn-neyvro.onrender.com/mcp
```

The expected Firebase verifier settings are the deployed issuer, Firebase
project audience, HTTPS Google JWKS URL, and Render resource URL. Do not put a
token on a command line because shell history and process listings can expose
it.

## 2. Verify a real token and the live MCP handshake

Interactive hidden input:

```bash
PYTHONPATH=src python3 scripts/verify_remote_auth.py
```

Piped input from a secret manager or a protected file descriptor:

```bash
secret_command_that_writes_only_to_stdout | PYTHONPATH=src \
  python3 scripts/verify_remote_auth.py
```

The utility performs all of the following:

- verifies the JWT through the same `JWTVerifier` used by the MCP server;
- checks RS256 signature, issuer, audience, expiry, issued-at, subject, JWKS,
  scope shape, and trusted workspace claim presence;
- identifies Firebase-ID-token compatibility versus an MCP resource-audience
  token without trusting unverified claims for authorization;
- verifies anonymous `/mcp` returns HTTP 401 with a protected-resource metadata
  challenge;
- sends an authenticated MCP `initialize` request using the supplied token;
- reports AWS authorization separately and always reports it false while the
  delegated backend bridge is disabled.

The token is never printed, logged, written to disk, or included in an error.
Exit code `0` means cryptographic verification and the authenticated MCP
handshake passed and a trusted workspace claim was present. Exit code `1`
means token or HTTP verification failed. Exit code `2` means configuration or
authorization is incomplete, including a valid Firebase token without a
trusted workspace claim.

## 3. Negative and regression tests

Run the complete local suite:

```bash
PYTHONPATH=src python3 -m pytest -q
```

The verifier tests cover invalid signatures, wrong issuer, wrong audience,
expired tokens, missing workspace identity, malformed scopes, missing scopes,
cross-tenant requests, JWKS key changes, anonymous HTTP challenges, and
protected-resource metadata. Live negative testing should use independently
issued invalid/expired/wrong-audience fixtures; never modify or forge a real
customer token in production.

## Interpretation

`CONFIGURED` means the provider settings are valid. `VERIFIED` means a real
token passed signature and claim validation in the running process. Neither
state proves Firebase workspace membership, AWS authorization, customer-data
access, or an interactive OAuth authorization-code/PKCE flow. Firebase is an
identity/token verification service, not by itself an MCP OAuth authorization
server.
