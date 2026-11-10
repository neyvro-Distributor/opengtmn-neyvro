# Remote MCP readiness

The repository now contains a production-oriented remote MCP boundary at `/mcp` using the official Python MCP SDK Streamable HTTP transport. It is separate from the local knowledge MCP server and fails closed when identity or backend configuration is absent.

## Startup

Install the package and configure the OAuth resource-server settings. The
backend variables are documented for deployment inventory, but do not activate
the adapter until the AWS delegated identity bridge is implemented.

```bash
python3 -m pip install -e .
NEYVRO_MCP_OAUTH_ISSUER=https://identity.example \
NEYVRO_MCP_OAUTH_AUDIENCE=neyvro-mcp \
NEYVRO_MCP_OAUTH_JWKS_URL=https://identity.example/.well-known/jwks.json \
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

- Incoming Firebase bearer tokens are verified against the explicitly configured HTTPS issuer/JWKS, RS256 signature, Firebase project audience, expiry, issued-at, and subject. Firebase ID tokens do not inherently carry a trusted Neyvro workspace claim, so private tools remain blocked until the backend identity bridge resolves workspace membership. The inbound token is never forwarded to the backend.
- Every tool declares a mode and required scopes. Proposal/approval tools require `proposals:write`; execution and publishing remain disabled unless a separately configured backend permits them.
- `workspace_id` is checked against the token tenant. No private company records are served by the local skill MCP.
- Proposal and external-action tools require an exact `approval_id`; a draft or proposal is never treated as sent.
- Website targets reject non-HTTP(S), local, loopback, and literal private-address targets. DNS rebinding protection and an egress proxy are still required before enabling live website research.
- Diagnostic logs go to stderr. Backend error bodies are bounded and token values are not logged.

## Readiness matrix

| Area | Status | Evidence / blocker |
|---|---|---|
| Official `/mcp` Streamable HTTP transport | VERIFIED | Uvicorn startup, MCP initialize handshake, and `tools/list` smoke test completed locally. |
| Tool schemas and bounded pagination | VERIFIED | 56 unique tool registrations expose Pydantic input/output schemas; page size is capped at 100. |
| OAuth JWT verification | CONFIGURED/VERIFIED | Configured environments report `CONFIGURED`; a real valid token is required before the process reports `VERIFIED`. No provider or token exchange is fabricated here. |
| Private customer-data authorization | BLOCKED | Health exposes this separately from authentication; the AWS delegated identity bridge is not deployed. |
| Backend service adapter | DISABLED | Static service credentials and a tenant header are intentionally insufficient; AWS must expose the delegated identity bridge in [BACKEND_AUTH_BRIDGE.md](BACKEND_AUTH_BRIDGE.md). |
| Tenant isolation | PARTIAL | Enforced at the remote boundary and covered by tests; production assurance depends on a backend adapter that cryptographically binds the service identity to the tenant. |
| Rate limits | PARTIAL | Process-local per-tenant/tool limiter exists; a shared store is required for multi-instance production. |
| Usage/cost controls | BLOCKED | No shared usage ledger or provider cost contract is present in the backend. Do not expose paid enrichment or research until this is supplied. |
| Audit logs | PARTIAL | Structured tool events are emitted to stderr; durable tenant audit storage and retention policy are not present. |
| Company/GTM/buyer read tools | PARTIAL | Existing discovery, onboarding, accounts, mailbox, and metrics routes are mapped, but endpoint semantics and service authentication are not yet MCP-ready. |
| Campaign execution and sending | DISABLED | Mailbox routes exist, but approved-payload, idempotency, reply-stop, and provider event guarantees are not available through a trusted MCP backend adapter. |
| LinkedIn/social publishing | DISABLED | No authorized official adapter; no scraping or browser automation is implemented. |
| CRM/pipeline/revenue attribution | PARTIAL/DISABLED | Account and operational metrics routes exist; CRM and revenue attribution contracts are missing. |
| SEO/GEO/content | DISABLED | Optional adapters and repository proposal service are not available. |

## Tool status

The server registers the requested tool catalog so clients can discover capabilities, but registration does not imply availability. Each tool exposes readiness metadata and returns `disabled`, `backend_unavailable`, `insufficient_scope`, `pending_approval`, or `available` explicitly. The backend adapter remains `DISABLED` until the trusted AWS bridge is deployed and verified; setting a backend URL or service credential alone cannot enable it.

## Required backend work before public customer-data exposure

1. Add an OAuth authorization-server/resource-server integration with PKCE, registered redirect URIs, issuer/audience/JWKS rotation, and tenant/workspace claims.
2. Add a trusted service-to-service identity exchange that the existing Firebase/session-cookie backend can validate; do not trust a caller-supplied tenant header alone.
3. Add shared rate-limit, usage, cost, idempotency, and durable audit stores.
4. Define stable response schemas and error contracts for every mapped endpoint.
5. Add backend tests for anonymous access, invalid credentials, missing scopes, tenant crossing, opt-out/reply-stop, SSRF, duplicate sends, and malicious source text.
6. Enable tools individually only after their adapter and integration tests reach `VERIFIED`.
