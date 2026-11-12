# AWS backend coordination handoff

AWS revision `3aca5d1` is available at the `mcp-bridge` branch. The Render
worktree did not modify it. To unblock local E2E, the AWS developer should
provide a running isolated API on `127.0.0.1:8001`, PostgreSQL 17 on
`127.0.0.1:5440`, the synthetic seed output, and test-only gateway/API public
keys identified as `gw-test-1` and `aws-test-1`. The revision includes
`ops/mcp/seed_world.py` and expanded `ops/mcp/local_check.py` real-record checks.

The API must be started with all 14 operations enabled. The test database must
be synthetic and end in `_mcp_dev`; production RDS is prohibited. The AWS
developer should also provide the reported 60/60 MCP test and 89/89 local HTTP
check evidence, plus database fingerprint evidence showing only audit,
replay and rate-limit bookkeeping changed.
