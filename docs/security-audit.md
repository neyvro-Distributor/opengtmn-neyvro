# Security audit

Date: 2026-10-23  
Result: NO-GO for public customer-data release.

| Control | Status | Evidence / limitation |
|---|---|---|
| Local MCP exposes no private records | PASS | Fixed skill root; public metadata/content only |
| OAuth issuer/audience/signature/expiry checks | PARTIAL | Implemented when configured; no production IdP available |
| Anonymous private-data rejection | PASS | Remote MCP tests |
| Scope enforcement | PASS | Per-tool scope checks and tests |
| Tenant mismatch rejection | PASS | Workspace/token tenant check and tests |
| Inbound token passthrough prevention | PASS | Server-side backend credential only; test coverage |
| Approval-gated proposal tools | PASS | Exact approval ID required |
| Unauthorized sends/publishing | PASS | Execution/publishing disabled by default |
| Duplicate-send/idempotency guarantee | BLOCKED | Trusted backend adapter and durable idempotency store absent |
| Reply/opt-out stop guarantee | BLOCKED | Provider event and scheduler integration absent |
| SSRF protection | PARTIAL | Literal private/local targets rejected; DNS rebinding/egress proxy remain |
| Cross-instance rate limiting | BLOCKED | Current limiter is process-local |
| Durable audit logs | BLOCKED | Current diagnostics are stderr only |
| Usage/cost controls | BLOCKED | No shared ledger/provider cost contract |
| Secrets in repository | PASS | Repository scans and fixture checks pass |
| Production TLS/health/monitoring | NOT_TESTED | No deployed endpoint |

No critical tenant-isolation bypass or authorization bypass was observed in the
available tests. That is not a production certification: the backend identity
exchange and shared control-plane stores must be added and tested before
release.
