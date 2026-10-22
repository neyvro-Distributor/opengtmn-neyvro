# MCP test report

## Local knowledge MCP

Status: PASS.

- Official Python MCP SDK `FastMCP` with stdio transport.
- 3 tools: `neyvro_list_skills`, `neyvro_get_skill`, `neyvro_search_skills`.
- 35 bounded skill resources at `neyvro://skills/<skill-name>`.
- 35 skill prompts.
- Tests cover initialization, `tools/list`, `tools/call`, resources, prompts,
  exact content, unknown IDs, invalid arguments, bounded content, and no
  filesystem-path leakage.
- Works without Neyvro authentication and exposes no customer data.

## Remote MCP boundary

Status: PARTIAL / BLOCKED for production deployment.

- Official Streamable HTTP app is present at `/mcp` and `/health`.
- 56 unique requested tool registrations with Pydantic request schemas,
  readiness metadata, scopes, modes, bounded pagination, and approval flags.
- Local tests cover anonymous rejection, tenant mismatch, missing scopes,
  pending approval, SSRF literal-address rejection, no inbound-token
  forwarding, and transport registration.
- A local Uvicorn initialize/`tools/list` smoke test was previously completed.
- No actual deployed HTTPS endpoint, OAuth issuer, service identity exchange,
  shared limiter, usage ledger, or production backend contract is available.

Tool registration is discovery only. Current backend availability is not
verified merely because a tool appears in `tools/list`.

## MCP Registry metadata

Status: PASS for schema validation, NOT_PUBLISHED for distribution. The draft
`.mcp/server.json` was validated against the official
`2025-12-11/server.schema.json`; it retains a deployment marker and does not
claim a published registry record.

## Complete synthetic customer workflow

Status: NOT_TESTED as a complete end-to-end workflow.

Existing unit tests cover isolated service and authorization behavior, but the
repository does not contain a verified two-tenant integration fixture spanning
onboarding through CRM revenue attribution. No real recipient was contacted.
This remains a release blocker rather than an implied success.
