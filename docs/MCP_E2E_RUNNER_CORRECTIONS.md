# MCP E2E runner corrections

## Fixed defects

- Tool arguments are derived from the advertised `tools/list` `inputSchema`.
  Servers that advertise a `request` object receive the required envelope;
  flat schemas remain flat. Arguments are validated before transport.
- The runner no longer uses hardcoded UUIDs. It discovers workspace, company,
  opportunity, conversation, and buyer identifiers from authorized synthetic
  responses and validates lowercase UUID formatting.
- HTTP 200 is not sufficient for success. The classifier checks JSON-RPC
  version/id, protocol errors, MCP `isError`, structured status, operation
  data, workspace identity, and sensitive-token absence.
- Expected security refusals have their own `PASS_EXPECTED_DENIAL` category;
  they never count toward positive-tool coverage.

## Classification

`PASS_POSITIVE` is an authorized business-data success. `PASS_EXPECTED_DENIAL`
is an expected negative authorization result. `FAIL_UNEXPECTED_DENIAL` means a
positive call was refused. `FAIL_PROTOCOL` and `FAIL_SCHEMA` identify transport
or contract defects. `BLOCKED` and `BLOCKED_MISSING_FIXTURE` identify missing
external prerequisites and are never passes.

## Firebase readiness

The runner accepts a Firebase ID token only through the environment variable
named by `--token-env` (default `NEYVRO_E2E_TOKEN_A`). The value is used in
memory, never printed, committed, or written to reports. Firebase setup,
allowlisting, server-managed grants, revocation, and cleanup are documented in
`docs/MCP_FIREBASE_TEST_SETUP.md`.
