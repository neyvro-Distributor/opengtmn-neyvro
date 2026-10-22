# Test evidence

Latest local run:

```text
make verify-all
mandatory skill gate: PASS (26 required, 35 packaged)
portable plugin validator: PASS; deployment: BLOCKED
skill build: PASS (35)
pytest: PASS (141 tests)
release decision: NO-GO
```

Covered tests include skill metadata/paths/related references, deterministic
builds, local MCP tools/resources/prompts, unknown-skill and invalid-input
handling, remote MCP scopes, tenant mismatch, approval gates, SSRF literal
targets, token non-forwarding, readiness, and client configuration parsing.

Not demonstrated by these tests:

- A live customer backend request.
- A real OAuth authorization-code/PKCE exchange.
- A deployed HTTPS MCP session.
- Live Gmail/Microsoft/CRM/enrichment/social provider behavior.
- A complete two-tenant workflow using real provider sandboxes.

Mocks and isolated fixtures are reported as test evidence only; they are not
reported as live integration verification.
