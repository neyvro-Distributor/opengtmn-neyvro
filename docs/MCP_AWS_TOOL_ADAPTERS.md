# MCP AWS tool adapters

## Contract boundary

The Render repository does not implement AWS business services. It is a thin,
fail-closed gateway over the AWS bridge contract. The current contract at
`48a308e` is sourced from the AWS repository at `1668dea` and defines only:

```text
companies.search
GET /v1/mcp/companies
scope: intelligence:read
```

The route returns workspace-filtered saved Discovery companies. It starts no
research, spends no credits, and persists nothing.

## Adapter registry

`ADAPTER_REGISTRY` in `src/neyvro/remote_mcp.py` is the only source of callable
private adapters. Each entry fixes the tool name, operation, HTTP method, path,
scope, output model, side-effect classification, credit classification,
timeout, retry policy, provider requirements, and feature flag.

The registry rejects drift between the adapter and `ToolSpec`. Paths are never
constructed from user input. The current registry deliberately contains one
entry. A future adapter must have an AWS contract route and tests before being
added.

## Request flow

1. MCP authentication verifies Token A as a Firebase RS256 identity and runs
   Firebase Admin revocation/disabled-account checking.
2. The adapter validates the fixed operation and bounded input.
3. Render creates a fresh ES256 Token B with `gateway+jwt`, `gw-1` (or
   `gw-test-1`), a UUID4 JTI, a 60-second lifetime, and the contract claims.
4. Render calls the fixed AWS exchange URL over HTTPS.
5. Render validates the exchange schema and uses Token C only as an opaque
   bearer for the same invocation.
6. Render calls the allowlisted route and validates the response model.
7. Render returns only sanitized company data. No token is logged or exposed.

Token C is never cached. AWS remains authoritative for workspace membership,
role, account state, operation enablement, scope, rate limits, and live access.

## Retry and timeout policy

There are no retries. The only implemented operation is an idempotent GET, but
retrying the exchange could create confusing one-use assertion behavior and is
not required by the contract. Timeouts are bounded by
`NEYVRO_MCP_BACKEND_TIMEOUT_SECONDS` and the adapter timeout.

## Extension rule

Do not add an adapter from an existing legacy path alone. AWS must first supply
an operation identifier, permission, route, request/response schema, workspace
semantics, error contract, side-effect and credit guarantees, and staging
tests. Until then classify the tool in
`docs/MCP_TOOL_INTEGRATION_MATRIX.md` and leave it disabled.
