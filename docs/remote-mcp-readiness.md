# Remote MCP readiness

The repository now contains a production-oriented remote MCP boundary at `/mcp` using the official Python MCP SDK Streamable HTTP transport. It is separate from the local knowledge MCP server and fails closed when Firebase identity or the AWS bridge configuration is absent.

## Startup

Install the package and configure the Firebase compatibility identity and AWS
bridge settings. The bridge remains disabled unless
`NEYVRO_MCP_BRIDGE_ENABLED=true` is explicitly set.

```bash
python3 -m pip install -e .
NEYVRO_MCP_FIREBASE_PROJECT_ID=neyvro-mcp-test \
NEYVRO_MCP_FIREBASE_SERVICE_ACCOUNT_JSON='<protected JSON>' \
NEYVRO_MCP_BRIDGE_ENABLED=false \
NEYVRO_MCP_RESOURCE_URL=https://mcp.example/mcp \
NEYVRO_MCP_ALLOWED_HOSTS=mcp.example \
neyvro-mcp-remote
```

The provider-assigned HTTPS URL can be used by an MCP client; a custom domain is not required. `neyvro-mcp-remote` runs the official Streamable HTTP transport. An ASGI target is also available as `neyvro.remote_mcp:REMOTE_APP` for a managed Uvicorn/Render deployment.

The unauthenticated `GET /health` endpoint returns service readiness metadata only; it does not return customer data.

For the repeatable live-token verification procedure, see
[PRODUCTION_AUTH_VERIFICATION.md](PRODUCTION_AUTH_VERIFICATION.md). It uses a
hidden or piped token input, checks the MCP 401 challenge, and performs an
authenticated `initialize` request without enabling the AWS adapter.

## Security boundary

- Incoming Firebase bearer tokens are verified against the fixed Google issuer/JWKS, RS256 signature, Firebase project audience, expiry, issued-at, auth time, and subject. Firebase Admin SDK revocation/disabled-account checking is required and fails closed. The inbound token is never forwarded to AWS.
- AWS receives a fresh ES256 `gateway+jwt` assertion for each invocation. Its issuer, audience, `kid`, operation, scope, workspace request, lifetime, and UUID JTI follow `docs/AWS_BRIDGE_CONTRACT.md`.
- Workspace membership and role are resolved by AWS on every exchange; a Firebase token never proves workspace membership. Only `neyvro_search_companies` is registered as a private tool.
- Proposal and external-action tools require an exact `approval_id`; a draft or proposal is never treated as sent.
- Website targets reject non-HTTP(S), local, loopback, and literal private-address targets. DNS rebinding protection and an egress proxy are still required before enabling live website research.
- Diagnostic logs go to stderr. Backend error bodies are bounded and token values are not logged.

## Readiness matrix

| Area | Status | Evidence / blocker |
|---|---|---|
| Official `/mcp` Streamable HTTP transport | VERIFIED | Uvicorn startup, MCP initialize handshake, and `tools/list` smoke test completed locally. |
| Tool schemas and bounded pagination | VERIFIED | The only enabled private tool validates query length and bounds page to 1..10000 and page size to 1..100. |
| Firebase identity verification | CONFIGURED/VERIFIED | Firebase Admin SDK configuration reports `CONFIGURED`; a real valid, non-revoked token is required before the process reports `VERIFIED`. |
| Workspace authorization | PER-CALL | AWS exchange resolves membership, role, active account, operation, and scope on every call. |
| AWS bridge adapter | DISABLED BY DEFAULT | It requires the explicit switch, fixed API URL, and gateway private key; it never uses a static bearer credential. |
| Tenant isolation | VERIFIED BY CONTRACT | Workspace selection is a request in Token B; AWS authorizes it and filters every company result by Token C's workspace. |
| Rate limits | PARTIAL | Process-local per-tenant/tool limiter exists; a shared store is required for multi-instance production. |
| Usage/cost controls | BLOCKED | No shared usage ledger or provider cost contract is present in the backend. Do not expose paid enrichment or research until this is supplied. |
| Audit logs | PARTIAL | Structured tool events are emitted to stderr; durable tenant audit storage and retention policy are not present. |
| Company discovery | AVAILABLE WHEN BRIDGE IS ENABLED | `neyvro_search_companies` maps only to `GET /v1/mcp/companies` and is read-only. |
| Other private tools and campaign execution | DISABLED | The remaining 55 private tool specs are retained only for readiness reporting and are not registered or callable. |
| LinkedIn/social publishing | DISABLED | No authorized official adapter; no scraping or browser automation is implemented. |
| CRM/pipeline/revenue attribution | PARTIAL/DISABLED | Account and operational metrics routes exist; CRM and revenue attribution contracts are missing. |
| SEO/GEO/content | DISABLED | Optional adapters and repository proposal service are not available. |

## Tool status

The server registers the public knowledge tools and only the first private tool. The remaining 55 private specs are not registered. The bridge remains `DISABLED` until the explicit switch, fixed API URL, gateway key, Firebase Admin configuration, and AWS deployment are verified.

## Required backend work before public customer-data exposure

1. Keep the AWS bridge branch deployed separately until the owner approves merge/go-live.
2. Configure new test Firebase and ES256 gateway keys; never reuse production keys.
3. Run the isolated API and `tests/test_mcp_bridge.py` from the AWS repository alongside this gateway's contract tests.
4. Enable the Render switch only after a two-workspace, revoked-member, missing-scope, replay, and cross-tenant staging run passes.
