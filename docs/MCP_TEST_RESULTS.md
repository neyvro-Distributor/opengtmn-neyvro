# MCP test results

Mock-based tests cover the 56-tool catalog, 30 enabled-tool allowlist, exact
operation/scope/route mappings, disabled tools, JWT verification, fresh
assertion boundaries, input validation, workspace selection, backend error
mapping, response-envelope validation and public skill regressions.

Current local result: `158 passed, 0 failed` with `PYTHONPATH=src pytest -q`.

Actual AWS end-to-end testing is not claimed: backend commit `abe22e7` is built
on `mcp-bridge` but is not deployed, and this workspace has no staging
Firebase project, isolated AWS database or test signing-key configuration.
