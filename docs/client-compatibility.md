# Client compatibility

The root `plugin.json`, `mcp.json`, `skills/`, and `LICENSE` are the canonical
distribution. Client-specific files are adapters or examples; they are not
alternate skill implementations.

| Client | Skills | MCP tools | Resources/prompts | OAuth | Status |
|---|---|---|---|---|---|
| OpenAI Codex | Tested | Registered against live endpoint | Package-dependent | OAuth provider unavailable | PARTIAL |
| Claude Code | Tested | Local package documented | Plugin/MCP support documented | OAuth provider unavailable | DOCUMENTED_ONLY |
| Cursor | Documented | Documented | Not live-tested | Documented by server/client flow | DOCUMENTED_ONLY |
| Windsurf / Devin Cascade | Documented via `.devin/skills` | Documented | Client-dependent | Documented | DOCUMENTED_ONLY |
| Cline | No native package test | Documented, Streamable HTTP | Client-dependent | Documented | DOCUMENTED_ONLY |
| Continue | No native skills test | Documented | Client-dependent | Not validated here | DOCUMENTED_ONLY |
| Zed | No native package test | Documented | Tools/prompts documented; resources not confirmed | Documented | DOCUMENTED_ONLY |
| VS Code GitHub Copilot | Documented via Agent Skills paths | Documented | Resources/prompts documented | Client/server-dependent | DOCUMENTED_ONLY |
| Gemini CLI | Documented and installable | Documented | MCP prompts documented by client | OAuth documented | DOCUMENTED_ONLY |

No client is marked `VERIFIED` for a real Neyvro customer-data call because the
deployment has no configured OAuth issuer or backend trust bridge. The live
endpoint and unauthenticated public skill surfaces are verified separately.

## Compatibility rules

- Portable skills are loaded from the canonical `skills/` directory or copied
  into a client's documented skill directory during installation.
- MCP clients may expose tools, resources, and prompts differently. The local
  Neyvro server implements all three, but each client must be checked before
  relying on a specific surface.
- OAuth is interactive where the client supports MCP OAuth discovery. Examples
  contain no bearer tokens, client secrets, or private records.
- Read, research, draft, propose, approve, execute, publish, and verify remain
  separate permission stages. Client-side auto-approval never grants a missing
  server-side permission.

See [Cursor installation](cursor-installation.md) and [other agents](other-agents.md).
