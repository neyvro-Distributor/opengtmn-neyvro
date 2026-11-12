# MCP test results

Mock-based tests cover the 56-tool catalog, 30 enabled-tool allowlist, exact
operation/scope/route mappings, disabled tools, JWT verification, fresh
assertion boundaries, input validation, workspace selection, backend error
mapping, response-envelope validation and public skill regressions.

Current local result: `161 passed, 0 failed` with `PYTHONPATH=src pytest -q`.

The 160 are mocked/unit tests only. The AWS contract suite was attempted with
`NEYVRO_DATABASE_URL=postgresql://...@127.0.0.1:5440/neyvro_mcp_dev` and
blocked before collection because PostgreSQL refused the connection.

Actual AWS end-to-end testing is not claimed: backend commit `abe22e7` is built
on `mcp-bridge` but is not deployed, and this workspace has no staging
Firebase project, isolated AWS database or test signing-key configuration.
