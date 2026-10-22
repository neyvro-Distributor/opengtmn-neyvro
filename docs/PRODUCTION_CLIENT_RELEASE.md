# Neyvro production client release

Status: **NO-GO for private customer-data access; transport/package release is ready for controlled testing.**

## Verified deployment

- Render service: `opengtmn-neyvro-`
- Deployment: `dep-dbd6qc8u01pc73bptarg` (`live`)
- MCP endpoint: `https://opengtmn-neyvro.onrender.com/mcp`
- Health: HTTP 200 from `/health`
- Runtime: Docker, `./Dockerfile`, port `$PORT`
- MCP initialize: PASS, protocol `2025-06-18`
- Tools: 56 discoverable
- Public skill resources: 35 discoverable/readable
- Prompts: 35 discoverable

## Release gates

| Gate | Status | Evidence |
|---|---|---|
| Portable package manifests | PASS | `plugin.json`, `mcp.json`, `.claude-plugin/` |
| Canonical skills | PASS | 26 mandatory; 35 packaged |
| Local knowledge MCP | PASS | 141 repository tests |
| Remote HTTPS transport | PASS | External initialize/list/read tests |
| Protected-resource OAuth metadata | BLOCKED | No issuer configured; metadata routes return 404 |
| PKCE login | BLOCKED | No production authorization server/client registration |
| MCP-to-backend trust bridge | BLOCKED | Backend uses Firebase ID token plus session cookie |
| Authenticated intelligence tools | DISABLED | Fail-closed by Render configuration |
| Production tenant isolation | NOT_TESTED | No authenticated two-tenant live fixture |
| Codex authenticated call | BLOCKED | Server registered, OAuth unavailable |
| Claude/Cursor/ChatGPT authenticated calls | NOT_TESTED | Requires provider and interactive client access |

The public endpoint is not evidence of customer-data authorization. Do not enable
private tools until OAuth, delegated backend identity, and tenant tests pass.

## Required external action

Provision a standards-compatible OAuth authorization server for the existing
Firebase-backed Neyvro identity model, configure issuer/audience/JWKS/resource
metadata in Render, then implement and verify the delegated backend assertion.
No secrets or tokens belong in this repository.
