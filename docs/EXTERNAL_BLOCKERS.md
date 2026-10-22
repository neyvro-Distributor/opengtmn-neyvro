# External blockers

These requirements cannot be verified from the current workspace without
external deployment, credentials, or provider authorization:

1. Provider-assigned HTTPS deployment for the remote `/mcp` service.
2. OAuth authorization server with PKCE, issuer metadata, JWKS, and tenant
   claims.
3. Trusted service-to-service identity exchange with the existing backend.
4. Shared rate limiting, usage/cost accounting, durable audit logs, and
   idempotency storage.
5. Gmail/Microsoft, enrichment, CRM, and social provider sandbox credentials.
6. Authenticated end-to-end calls from Cursor and other external clients.
7. Verified namespace/publisher authentication for MCP Registry publication.

No external blocker is represented as a successful implementation. Until these
items are supplied, the remote service remains fail-closed and external sends,
publishing, enrichment, and customer-data access remain disabled or partial.
