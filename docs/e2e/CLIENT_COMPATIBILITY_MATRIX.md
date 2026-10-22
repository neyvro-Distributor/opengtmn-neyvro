# Client compatibility matrix

This matrix records executed evidence, not intended support. A registration or
`tools/list` result is not an authenticated customer-data test.

| Platform | Install | OAuth | Discover | Real tool call | Tenant safe | Result |
|---|---|---|---|---|---|---|
| Codex CLI | PASS | BLOCKED | PASS | BLOCKED | NOT_TESTED | PARTIAL |
| Codex plugin | PASS | BLOCKED | NOT_TESTED | BLOCKED | NOT_TESTED | BLOCKED |
| ChatGPT plugin | DOCUMENTED_ONLY | BLOCKED | NOT_TESTED | NOT_TESTED | NOT_TESTED | BLOCKED |
| Claude Code MCP | DOCUMENTED_ONLY | BLOCKED | NOT_TESTED | NOT_TESTED | NOT_TESTED | BLOCKED |
| Claude Code plugin | PASS manifest | BLOCKED | NOT_TESTED | NOT_TESTED | NOT_TESTED | DOCUMENTED_ONLY |
| Claude app | DOCUMENTED_ONLY | BLOCKED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED |
| Cursor IDE | PASS example | BLOCKED | NOT_TESTED | NOT_TESTED | NOT_TESTED | DOCUMENTED_ONLY |
| Cursor plugin | DOCUMENTED_ONLY | BLOCKED | NOT_TESTED | NOT_TESTED | NOT_TESTED | DOCUMENTED_ONLY |
| VS Code | PASS example | BLOCKED | NOT_TESTED | NOT_TESTED | NOT_TESTED | DOCUMENTED_ONLY |
| Gemini CLI | PASS example | BLOCKED | NOT_TESTED | NOT_TESTED | NOT_TESTED | DOCUMENTED_ONLY |
| Windsurf | PASS example | BLOCKED | NOT_TESTED | NOT_TESTED | NOT_TESTED | DOCUMENTED_ONLY |

Shared verified evidence: live endpoint, health 200, MCP initialize, 56 tools,
35 resources, 35 prompts, and anonymous protected-tool rejection. No client has
completed OAuth or retrieved private Neyvro data.
