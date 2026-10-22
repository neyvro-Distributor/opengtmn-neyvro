# OAuth client compatibility

The Neyvro MCP endpoint currently has no configured OAuth issuer. Therefore all
client OAuth results below are blocked by the same server-side dependency, not by
client-specific workarounds.

## Intended configuration

Clients should connect to:

`https://opengtmn-neyvro.onrender.com/mcp`

The future authorization server must support Authorization Code + PKCE S256,
issuer/audience validation, JWKS, tenant claims, and scopes such as
`intelligence:read`. The provider's actual issuer, metadata URLs, client
registration mode, and redirect URIs must be supplied before publishing them.

## Current evidence

- Live MCP discovery succeeds without customer data.
- Unauthenticated protected-tool calls are rejected with
  `missing_or_invalid_oauth`.
- `/.well-known/oauth-protected-resource` currently returns HTTP 404 because no
  OAuth configuration is present.
- `/.well-known/oauth-authorization-server`, `/oauth/authorize`, and
  `/oauth/token` also return HTTP 404.
- No bearer token, client secret, or provider URL has been fabricated.

## Client status

| Client | Installation/configuration | OAuth | Authenticated data call |
|---|---|---|---|
| Codex CLI | Registered | BLOCKED | BLOCKED |
| Claude Code | Documented | BLOCKED | NOT_TESTED |
| Cursor | Configured example | BLOCKED | NOT_TESTED |
| ChatGPT custom MCP | Documented | BLOCKED | NOT_TESTED |
| VS Code | Valid example | BLOCKED | NOT_TESTED |
| Gemini CLI | Valid example | BLOCKED | NOT_TESTED |
| Windsurf/Cline | Valid examples | BLOCKED | NOT_TESTED |

Official references: [OpenAI Agent Plugins](https://developers.openai.com/plugins/build/plugins),
[OpenAI custom MCP](https://developers.openai.com/api/docs/guides/custom-mcp-server),
[Claude MCP](https://docs.anthropic.com/en/docs/mcp),
[Cursor customization](https://cursor.com/docs/customize-cursor), and
[VS Code MCP servers](https://code.visualstudio.com/docs/agent-customization/mcp-servers).
