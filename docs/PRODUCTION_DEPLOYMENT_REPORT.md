# Neyvro MCP live production deployment report

Date: 2026-10-23

| Area | Status |
|---|---|
| Render workspace | BLOCKED — current Render token expired (`401 Unauthorized`) |
| Neyvro MCP service | BLOCKED — no service could be inspected with the current token |
| Public HTTPS endpoint | BLOCKED — none exists in repository configuration |
| MCP protocol | PASS locally; public deployment NOT TESTED |
| OAuth/PKCE | BLOCKED — no production issuer configured |
| Backend trust bridge | BLOCKED — existing backend uses Firebase/session cookies |
| Tenant isolation | PASS at local boundary tests; production two-tenant test NOT TESTED |
| Working intelligence tools | 0 production-verified; local contracts exist but adapter is fail-closed |
| Codex connection | BLOCKED — no endpoint configured |
| ChatGPT connection | BLOCKED — no endpoint/OAuth configured |
| Regression tests | PASS — 141 repository tests; 225 backend targeted tests |
| Customer beta | NO-GO |

The checked-in Dockerfile, `$PORT` startup command, `/health` route, and
Streamable HTTP `/mcp` boundary were inspected. No customer-data deployment
was claimed. Private tools remain disabled.
