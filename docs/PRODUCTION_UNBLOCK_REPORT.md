# Neyvro MCP production unblock report

Date: 2026-10-23

## Decision

**NO-GO for customer-data production exposure.** The local knowledge MCP and
the remote MCP boundary are implemented and validated, but the customer-facing
authenticated path is not deployable yet.

## Verified

- 26 mandatory skills and 35 packaged skills validate successfully.
- 56 remote tool contracts are registered.
- The repository test suite passes: 141 tests.
- The actual Neyvro backend targeted suite passes: 225 tests.
- Render Blueprint validation passes for the Docker web service `mcp-gateway`.
- Local Streamable HTTP health and MCP initialization/tool discovery were tested.

## Blocked

- Actual deployed URL: **none**. Render has no deployed Neyvro MCP/API service.
- OAuth issuer/PKCE: **not configured**. The backend currently uses Firebase
  authentication followed by Neyvro session cookies.
- MCP-to-backend identity exchange: **not implemented**. The current adapter's
  service-token path is intentionally disabled without a trusted backend
  contract.
- Codex authenticated invocation: **not tested**; no endpoint is configured.
- ChatGPT invocation: **not tested**; no endpoint or OAuth provider exists.

Private-data tools remain fail-closed. No credentials, customer records, or
fake deployment results were used.

## Required release actions

Provision the OAuth authorization/resource-server integration, implement the
trusted tenant-bound backend exchange, authorize a scoped repository release,
create the validated Render service, then rerun the live client tests.
