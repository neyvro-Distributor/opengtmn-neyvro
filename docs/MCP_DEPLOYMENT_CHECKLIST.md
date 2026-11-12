# MCP deployment and rollback checklist

Before staging, deploy AWS `mcp-bridge` commit `abe22e7` to an isolated
environment, generate separate gateway/API P-256 key pairs, seed synthetic
Firebase users and two workspaces, and keep the bridge disabled during smoke
tests.

Required Render settings: `NEYVRO_MCP_BRIDGE_ENABLED`,
`NEYVRO_MCP_API_BASE_URL`, `NEYVRO_MCP_GATEWAY_PRIVATE_KEY`,
`NEYVRO_MCP_GATEWAY_KEY_ID`, `NEYVRO_MCP_FIREBASE_PROJECT_ID`,
`NEYVRO_MCP_FIREBASE_SERVICE_ACCOUNT_JSON`, `NEYVRO_MCP_RESOURCE_URL`,
`NEYVRO_MCP_ALLOWED_HOSTS`, `NEYVRO_MCP_ALLOWED_API_HOSTS`, and
`NEYVRO_MCP_BACKEND_TIMEOUT_SECONDS`.

Run `PYTHONPATH=src pytest -q`, then section 15 of the AWS contract: all 14
operations, authorized and negative membership/mailbox cases, replay/expiry/
wrong-operation checks, schema checks, audit-token absence, and no-write/
no-credit verification. Roll back by setting the bridge flag false, restarting
Render, and verifying every private tool is disabled. Rotate both key IDs if
compromise is suspected. Do not merge or deploy from this branch.
