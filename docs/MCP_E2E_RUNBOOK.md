# Local MCP E2E runbook

1. Use an isolated AWS worktree at `mcp-bridge` revision `3aca5d1`.
2. Start PostgreSQL 17 on loopback port `5440` with a database ending in
   `_mcp_dev`; run migrations, `ops/mcp/seed_test_data.py`, and the latest
   revision's `ops/mcp/seed_world.py` for real records.
3. Generate independent test-only P-256 key pairs: gateway `gw-test-1`, AWS
   `aws-test-1`; never print private keys.
4. Configure a separate Firebase test project and verified synthetic users,
   then configure exact server-managed grants.
5. Start the API on `127.0.0.1:8001` with all 14 operations enabled.
6. Start the Render MCP gateway on loopback with the test grant and API-key
   configuration.
7. Run the AWS `ops/mcp/local_check.py` first, then run
   `scripts/run_mcp_real_e2e.py`; inspect both generated reports.
8. Repeat with Alpha/Beta, revoked grants, removed members, mailbox access,
   replay, expiry, wrong operation and backend-offline cases.
9. Stop local processes and remove only the isolated test database/data volume.

The runner exits `2` for blocked or failed verification and `0` only when every
tool call is `PASS_POSITIVE`. A missing resource fixture is reported as
`BLOCKED_MISSING_FIXTURE`; do not replace it with a guessed UUID. Synthetic
handler tests must never be reported as real cross-service E2E.

For negative checks, invoke the classifier with an explicit expected-denial
scenario. `PASS_EXPECTED_DENIAL` is a security-test pass, not a business-data
pass. Keep those results in a separate report section.
