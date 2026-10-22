# Security test results

## Verified locally

- Anonymous remote tool access is rejected.
- Missing scopes are rejected.
- Tenant mismatch is rejected.
- Approval-gated tools fail closed without an approval ID.
- Literal local/private website targets are rejected.
- Inbound OAuth tokens are not forwarded to the backend.
- Public skill resources contain no customer records.
- External sending remains disabled.

## Not verified in production

- Two real organizations through the deployed backend.
- OAuth token revocation and refresh.
- Shared multi-instance rate limits and durable audit storage.
- Provider deployment logs and restart behavior.
- Real authorized company/opportunity/evidence records.

Any unverified production security gate blocks customer beta.
