# MCP authorization handoff

## AWS dependencies

No AWS code changes are requested. The AWS bridge must continue to treat Token
B as a gateway assertion and remain authoritative for canonical Firebase UID,
active account, membership, role, operation, workspace and mailbox access.

## Required infrastructure

- Separate Firebase test project with verified synthetic users and Admin SDK
  revocation checks.
- Approved external OAuth authorization server supporting authorization code,
  PKCE S256, resource indicators/audience, consent and revocation.
- Protected Render settings: `NEYVRO_MCP_OAUTH_ISSUER`,
  `NEYVRO_MCP_OAUTH_AUDIENCE`, `NEYVRO_MCP_OAUTH_JWKS_URL`,
  `NEYVRO_MCP_RESOURCE_URL`, and issuer-qualified
  `NEYVRO_MCP_OAUTH_IDENTITY_BINDINGS_JSON`.
- Firebase test-only settings only in an isolated environment:
  `NEYVRO_MCP_FIREBASE_TEST_MODE` and
  `NEYVRO_MCP_FIREBASE_TEST_GRANTS_JSON`.

Current status is **NO-GO** for production authorization. Real provider
consent, refresh/revocation, client registration and Token A→B→C E2E remain
unverified.
