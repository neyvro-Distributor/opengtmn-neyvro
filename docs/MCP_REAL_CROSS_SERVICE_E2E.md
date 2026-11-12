# Real cross-service MCP E2E

## Current result

**BLOCKED**. AWS branch `mcp-bridge` revision `3aca5d1` is reachable, but no
local FastAPI process is listening on `127.0.0.1:8001` and PostgreSQL is not
listening on `127.0.0.1:5440`. No gateway/backend tool call was represented as
real E2E.

The loopback-only runner is `scripts/run_mcp_real_e2e.py`. It performs health
checks, MCP initialize, `tools/list`, schema-driven resource discovery, and
`tools/call` for all 30 tools when a real test Token A and both local services
are available. It writes JSON and Markdown reports and never prints the token.

The runner now requires the advertised input schema. If a server advertises a
top-level `request` object, arguments are wrapped as
`{"request": {...}}`; otherwise the advertised flat shape is used. Each
request is validated before it is sent. Resource IDs are learned from
authorized synthetic responses; invented UUIDs are never used.

Positive calls are `PASS_POSITIVE` only when the JSON-RPC id, MCP result,
`structuredContent.status`, contract data, workspace, and response safety
checks all pass. `isError: true` and structured denial statuses cannot pass a
positive call. A denial is `PASS_EXPECTED_DENIAL` only in an explicitly
negative security scenario.

Run:

```bash
NEYVRO_E2E_TOKEN_A='<test token supplied out of band>' \
  PYTHONPATH=src python3 scripts/run_mcp_real_e2e.py
```

With current prerequisites the safe expected result is `BLOCKED`, with all 30
tools individually marked `BLOCKED`.

The current environment has no shared access to the AWS developer's loopback
services and no `NEYVRO_E2E_TOKEN_A`, so genuine Firebase Token A, Token B/C,
AWS authorization, and business-data results remain **BLOCKED**, not passed.
