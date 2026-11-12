# Real cross-service MCP E2E

## Current result

**BLOCKED**. AWS branch `mcp-bridge` revision `3aca5d1` is reachable, but no
local FastAPI process is listening on `127.0.0.1:8001` and PostgreSQL is not
listening on `127.0.0.1:5440`. No gateway/backend tool call was represented as
real E2E.

The loopback-only runner is `scripts/run_mcp_real_e2e.py`. It performs health
checks, MCP initialize, `tools/list`, and `tools/call` for all 30 tools when a
real test Token A and both local services are available. It writes JSON and
Markdown reports and never prints the token.

Run:

```bash
NEYVRO_E2E_TOKEN_A='<test token supplied out of band>' \
  PYTHONPATH=src python3 scripts/run_mcp_real_e2e.py
```

With current prerequisites the safe expected result is `BLOCKED`, with all 30
tools individually marked `BLOCKED`.
