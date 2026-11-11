# MCP test results

## Local results

Run from the implementation worktree:

```bash
PYTHONPATH=src python3 -m pytest -q
make verify-all
```

Current result: **161 passed, 0 failed**. Repository validation, plugin
validation, skill build, and diff checks also pass.

## Covered security behavior

The mocked adapter tests cover:

- Firebase RS256 signature, issuer, audience, expiry, `auth_time`, subject,
  and Firebase Admin revocation fail-closed behavior.
- Exact ES256 gateway header and claims, including `gateway+jwt`, key id,
  operation, scope, lifetime, and fresh cryptographic JTI values.
- Invalid signing key handling without parser-detail disclosure.
- No Firebase token forwarding, no AWS token in MCP output, and no token logs.
- Missing scope, disabled tools, workspace-selection responses, and response
  workspace mismatch protection.
- AWS 401, 403, 409, 429, and 503 mappings; timeout and malformed responses.
- Query and pagination bounds, typed response validation, and public-tool
  regression behavior.
- All 55 unsupported private tools remain disabled and absent from the callable
  MCP registry.

## Not claimed as tested

The AWS repository's live database replay table, rate counters, audit rows,
Token C verification, revoked membership behavior, and cross-tenant database
filtering require the AWS staging service. No live AWS or Render deployment was
used for this change. Mock tests do not prove production AWS behavior.

## Staging test sequence

Use a separate Firebase project, isolated AWS database, `gw-test-1`, `aws-test-1`,
and a loopback or approved staging API. Execute two workspaces and test:

1. Owner/member/viewer authorized search.
2. Missing `intelligence:read`, revoked member, disabled user, and suspended account.
3. No workspace, multiple workspaces, selected wrong workspace, and cross-tenant data.
4. Replayed JTI, expired assertion, wrong issuer/audience, invalid key, and swapped tokens.
5. AWS 401/403/409/429/503, timeout, malformed response, and oversized response.
6. Confirm AWS audit rows contain identifiers only and no token material.
