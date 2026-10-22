# MCP protocol results

## Local knowledge MCP

Status: PASS.

The official MCP Python SDK and stdio transport were exercised by
`tests/test_mcp_server.py` using a real `ClientSession`. The test verified:

- initialization;
- `tools/list` and all three tools;
- `tools/call` for listing, exact loading, and search;
- 35 bounded resources and exact `SKILL.md` content;
- 35 prompts and prompt retrieval;
- invalid limits and unknown skill errors;
- no filesystem paths in public metadata.

## Local remote HTTP boundary

Status: PARTIAL.

The application started with:

```bash
PYTHONPATH=src python3 -m uvicorn neyvro.remote_mcp:REMOTE_APP \
  --host 127.0.0.1 --port 8765
```

The real loopback request `GET http://127.0.0.1:8765/health` returned HTTP JSON
with `status: ok`, `authentication: BLOCKED`, and
`backend_service_adapter: DISABLED`. The remote app exposes `/mcp`, 56 tool
contracts, 35 public resources, and 35 public prompts.

The local protocol and authorization tests pass, but no authenticated remote
customer-data call was possible. The MCP Inspector command was not completed
because the environment could not finish the `npx` package resolution; this is
recorded as NOT_TESTED rather than PASS.
