# MCP security audit

## Verified locally

- Token B uses ES256, exact issuer/audience/type/key ID, exact operation and
  scope, a fresh UUID JTI, and a maximum 60-second lifetime.
- Token A verification uses RS256, issuer/audience/signature/time/subject
  checks; Firebase mode requires `auth_time` and resets readiness on failed
  verification. Admin revocation remains fail-closed when configured.
- Token A is never sent to AWS; Token C is opaque and never returned or logged.
- Firebase `scope`/`scp` claims are not authorization grants; only explicit
  isolated test grants can authorize Firebase compatibility users.
- External OAuth subjects require issuer-qualified server-side identity
  bindings before they can become AWS Firebase UIDs.
- Firebase and external OAuth trust modes fail closed when both are configured.
- Backend URL, method and operation are allowlisted; redirects are disabled;
  non-HTTPS non-loopback API hosts are rejected.
- UUIDs, pagination, filters, response size and contract envelope are bounded.
- Unsupported tools cannot reach the backend adapter.

## Not yet proven E2E

AWS must still prove Token C signature/operation/workspace checks, replay
protection, live membership revocation, mailbox authorization, audit redaction
and database/provider no-write behavior. These require the isolated API and
PostgreSQL stack.

## Findings fixed

1. **High — Firebase verifier regression:** restored the missing parent
   verification assignment and added a missing-`auth_time` regression test.
2. **Medium — buyer projection boundary:** buyer lookup now requires
   `buyer_id` and returns only the selected person.
3. **Medium — response boundary:** oversized responses are rejected and
   404/bridge-unavailable errors are mapped safely.
