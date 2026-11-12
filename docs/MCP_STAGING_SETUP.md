# MCP isolated staging setup

The AWS contract provides a safe local setup; no hosted staging exists.

1. Start isolated PostgreSQL 17 bound only to `127.0.0.1:5440`, using an empty
   database ending in `_mcp_dev`.
2. In the AWS worktree run `uv sync --locked`, `uv run alembic upgrade head`,
   and `uv run python ../../ops/mcp/seed_test_data.py` with synthetic UIDs.
3. Generate separate P-256 keys with IDs `gw-test-1` and `aws-test-1`.
4. Create a separate Firebase test project and verified synthetic users. A
   synthetic JWT fixture is not Firebase E2E.
5. Start the API on `127.0.0.1:8001` with all 14 operations switched on, run
   `ops/mcp/local_check.py`, then point the Render gateway at that loopback API.
6. Exercise Alpha/Beta isolation, revoked/disabled/no-membership users,
   mailbox access, wrong operation, replay, expiry and schema cases. Fingerprint
   business tables before and after every read.

Current blocker: PostgreSQL is not running on `127.0.0.1:5440`; no startup,
seed, API process or local HTTP E2E was performed.
