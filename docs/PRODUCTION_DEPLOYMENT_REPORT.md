# Neyvro MCP live production deployment report

Date: 2026-10-23

| Area | Status |
|---|---|
| Render workspace | VERIFIED — My Workspace (`tea-dbd6d1rl550s73ar8te0`) |
| Neyvro MCP service | LIVE — `opengtmn-neyvro` (`srv-dbd6flafngtc73fph450`) |
| Public HTTPS endpoint | VERIFIED — `https://opengtmn-neyvro.onrender.com/mcp` |
| MCP protocol | PASS — external initialize, tools/list, resources/list/read, prompts/list |
| OAuth/PKCE | BLOCKED — no production issuer configured |
| Backend trust bridge | BLOCKED — existing backend uses Firebase/session cookies |
| Tenant isolation | PASS at local boundary tests; production two-tenant test NOT TESTED |
| Working intelligence tools | 0 production-verified; local contracts exist but adapter is fail-closed |
| Codex connection | PARTIAL — server registered; OAuth authentication unsupported |
| ChatGPT connection | BLOCKED — no endpoint/OAuth configured |
| Regression tests | PASS — 141 repository tests; 225 backend targeted tests |
| Customer beta | NO-GO |

Deployment `dep-dbd6p43bc2fs73a1eug0` is live for commit `db8bb58d…`.
External health returned HTTP 200. An unauthenticated live tool call was
rejected with `missing_or_invalid_oauth`. Private tools remain disabled.
