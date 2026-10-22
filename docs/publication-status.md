# Publication status

| Artifact | Status | Reason |
|---|---|---|
| Portable `plugin.json` | PASS | Local schema/manifest validation passes |
| Codex compatibility package | PASS | Local package and installer checks pass |
| Claude Code package | PASS | Local manifest validation previously passed |
| Cursor compatibility | DOCUMENTED_ONLY | No headless authenticated Cursor session |
| Local knowledge MCP | PASS | Protocol tests pass without login |
| Remote MCP deployment | BLOCKED | No actual HTTPS host or OAuth issuer |
| MCP Registry `server.json` draft | PASS | Validated against official 2025-12-11 schema; explicitly unpublished |
| Official MCP Registry publication | BLOCKED | Namespace ownership, deployment, and publisher auth not verified |
| Plugin marketplaces | BLOCKED | Separate client approval/submission processes not completed |

The `.mcp/server.json` file intentionally uses a deployment marker and
`releaseStatus: not-published`. Registry metadata does not install a server in
Codex, Claude, Cursor, or other clients.
