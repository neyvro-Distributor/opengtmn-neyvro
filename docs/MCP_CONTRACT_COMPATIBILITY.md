# MCP contract compatibility report

Compared against AWS repository `neyvro`, branch `mcp-bridge`, commit
`abe22e7`, using its published OpenAPI contract.

Command:

```bash
PYTHONPATH=src python3 scripts/verify_mcp_contract.py \
  /Users/ankitpandey/neyvro-backend-contract/docs/integrations/mcp-bridge.openapi.json
```

Result: **PASS — 14 operations match**. The check verifies operation set,
route, `GET` method, scope, read-only and credit flags, query/path parameter
names, `200` responses and required error statuses.

Render validates the contract envelope and operation-specific required fields.
Full nested JSON-schema validation remains an AWS/OpenAPI integration gate and
is not claimed locally without the backend service.

All 14 operations are represented in `OPERATION_ADAPTERS`; 30 MCP tools are
represented in `ADAPTER_REGISTRY`. `signals.list` and `analytics.get` are
contract operations without a direct legacy MCP tool mapping, as specified by
the AWS section-14 matrix.
