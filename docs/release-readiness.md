# Release readiness

## Final assessment: NO-GO

The local knowledge package is releasable as a pre-release artifact. The public
customer-data plugin and remote MCP are not ready for production because the
remote deployment, OAuth authorization service, trusted backend identity
exchange, shared rate/usage/audit controls, and complete provider workflow are
not present.

### Gate summary

| Gate | Status |
|---|---|
| Mandatory 26 skills present and substantive | PASS |
| 35-skill registry/build validation | PASS |
| Local MCP protocol behavior | PASS |
| Remote Streamable HTTP implementation | PARTIAL |
| OAuth discovery and production identity | BLOCKED |
| Tenant isolation at boundary | PASS (tested boundary) / PARTIAL (backend) |
| Unauthorized send/publish prevention | PASS (disabled by default) |
| Complete two-tenant workflow | NOT_TESTED |
| Real external MCP client with authenticated Neyvro read call | BLOCKED |
| Production hosting/TLS/monitoring | NOT_TESTED |
| Registry publication | BLOCKED |

## Actual endpoints

- Local stdio command: `neyvro-mcp-skills`.
- Remote endpoint: none deployed.
- Local test-only ASGI endpoint: `/mcp` when `neyvro-mcp-remote` is started;
  this is not a public endpoint.

## Required release blockers

1. Deploy the remote service on existing Neyvro hosting and record the actual
   provider-assigned HTTPS URL.
2. Configure and test OAuth authorization metadata, PKCE, issuer/audience/JWKS
   rotation, and tenant claims.
3. Implement the trusted backend service identity exchange.
4. Add shared rate limits, usage/cost budgets, durable audit events, and
   idempotency keys.
5. Complete two synthetic-tenant integration tests, including opt-out/reply
   stops and CRM attribution.
6. Run at least one real external MCP client against a read-only deployed tool.
7. Validate and publish the registry entry only after namespace ownership and
   deployment are verified.

## Rollback plan

Keep the remote MCP service disabled or remove its hosting deployment, revoke
the OAuth client/resource registration, and revert the release tag to the last
known package revision. Because sending/publishing adapters are disabled by
default, rollback does not require cancelling live customer sends. A production
release must add a tested migration and provider-event rollback procedure.
