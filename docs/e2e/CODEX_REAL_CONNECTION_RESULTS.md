# Codex real connection results

Status: BLOCKED for real Neyvro connection; local package validation PASS.

Observed environment:

- Codex CLI: `codex-cli 0.163.0`.
- `codex mcp list --json` completed successfully.
- No `neyvro` MCP entry is configured.
- Existing unrelated MCP entries were not modified.

The required registration and agent-session tests were not attempted because no
real Neyvro HTTPS endpoint exists. A deployment marker must never be passed to
Codex as if it were a live URL.

After deployment, run with the actual URL:

```bash
codex mcp add <server-name> --url "https://<actual-host>/mcp"
codex mcp list
codex mcp login <server-name> --oauth-client-registration dcr
```

Replace the displayed server label with the exact supported name; complete
interactive OAuth, then test a read-only tool in a real Codex session. Current
status is not a Codex failure; it is an external deployment/authentication
blocker.
