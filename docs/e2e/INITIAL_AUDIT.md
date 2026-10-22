# Initial E2E audit

Date: 2026-10-23 (Asia/Kolkata)  
Repository: `opengtmn-neyvro-`  
Reference OpenGTM commit: `fedfaebbfbc435c671ec6298dbe0a40a07f9b5d0`

| Check | Status | Evidence |
|---|---|---|
| Local MCP implementation | PASS | `src/neyvro/mcp_server.py`, official Python MCP SDK |
| Remote MCP implementation | PASS | `src/neyvro/remote_mcp.py`, Streamable HTTP app |
| Public remote deployment | BLOCKED | `mcp.json` retains deployment marker; no hosted URL |
| OAuth authorization server | BLOCKED | JWT verifier exists; issuer/PKCE service absent |
| 26 mandatory skills | PASS | `scripts/validate_release.py` |
| Local MCP protocol tests | PASS | Official `ClientSession` test suite |
| Backend live integration | BLOCKED | No trusted backend service credential/exchange |
| Codex CLI installed | PASS | `codex-cli 0.163.0` |
| Codex Neyvro connection | NOT_TESTED | No real endpoint; no placeholder registration performed |
| ChatGPT custom MCP connection | BLOCKED | Requires deployed endpoint and interactive account authorization |
| External provider sandboxes | BLOCKED | No Gmail/Microsoft/CRM/enrichment credentials |

No credentials, tokens, customer records, or fictional endpoint are included in
the evidence.
