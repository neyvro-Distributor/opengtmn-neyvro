# Security test results

| Test | Status | Evidence |
|---|---|---|
| Anonymous private-tool access | PASS | Remote MCP tests |
| Missing scope | PASS | Remote MCP tests |
| Wrong tenant | PASS | Remote MCP tests |
| Approval required for proposals | PASS | Remote MCP tests |
| Inbound token passthrough | PASS | Backend adapter test |
| Local/private SSRF literals | PASS | Website-target test |
| Unsupported execution | PASS | Fail-closed readiness |
| Live expired/revoked OAuth token | NOT_TESTED | No production issuer |
| Duplicate dispatch/idempotency | BLOCKED | No trusted scheduler/store |
| Reply/opt-out stop against provider events | BLOCKED | No mailbox event adapter |
| Cross-tenant backend database query | BLOCKED | No service identity exchange |
| Production rate limits/audit logs | BLOCKED | Process-local controls only |

No credentials or customer records were used. These results do not certify
production security while the BLOCKED controls remain unresolved.
