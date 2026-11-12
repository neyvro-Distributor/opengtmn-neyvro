# MCP deployment readiness

## Decision: NO-GO

The Render implementation is ready for continued isolated testing only. Do
not merge, deploy or enable production features.

Required before GO: isolated AWS API/database from `abe22e7`; synthetic
Firebase users; separate `gw-test-1`/`aws-test-1` keys and rotation tests; all
14 operations and 30 tools exercised over local HTTP; Alpha/Beta isolation;
membership revocation; mailbox access checks; no-write/no-credit evidence; and
an external MCP OAuth server with resource audience and PKCE.

Required Render names include `NEYVRO_MCP_BRIDGE_ENABLED`,
`NEYVRO_MCP_API_BASE_URL`, `NEYVRO_MCP_ALLOWED_API_HOSTS`,
`NEYVRO_MCP_GATEWAY_PRIVATE_KEY`, `NEYVRO_MCP_GATEWAY_KEY_ID`,
`NEYVRO_MCP_FIREBASE_PROJECT_ID`, `NEYVRO_MCP_FIREBASE_SERVICE_ACCOUNT_JSON`,
`NEYVRO_MCP_RESOURCE_URL`, `NEYVRO_MCP_ALLOWED_HOSTS`,
`NEYVRO_MCP_BACKEND_TIMEOUT_SECONDS`, `NEYVRO_MCP_REQUESTS_PER_MINUTE`, and
`NEYVRO_MCP_PUBLIC_REQUESTS_PER_MINUTE`.

Rollback: set `NEYVRO_MCP_BRIDGE_ENABLED=false`, restart Render, verify all
private tools are disabled, and rotate gateway/API key IDs if compromise is
suspected.
