# MCP scope grant policy

Supported read scopes:

- `intelligence:read`: approved non-mail read-only operations.
- `mail:read`: conversations and mailbox overview subject to AWS mailbox access.

Reserved and inactive: `proposals:write`, `research:run`.

Firebase ID-token claims named `scope` or `scp` are never trusted as grants.
The only Firebase compatibility grant source is the exact server-managed,
test-only UID map enabled by `NEYVRO_MCP_FIREBASE_TEST_MODE=true` for a project
whose name contains `test`. Grants are bounded, may expire or be revoked, and
never apply to every authenticated user.

External OAuth scopes are accepted only from a signature-verified token issued
by the configured authorization server/resource audience. Unknown scopes are
not effective. Missing or expired grants fail closed before AWS exchange.
