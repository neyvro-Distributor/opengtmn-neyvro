# MCP AWS tool adapters

`ADAPTER_REGISTRY` is the only callable private-adapter allowlist. It is
derived from the 30-tool mapping and 14 contract operation definitions. Each
entry fixes the operation, `GET` method, route, scope, read-only classification
and no-credit guarantee; legacy routes are not fallbacks.

Each invocation verifies Token A, signs a fresh ES256 Token B for the exact
operation, exchanges it, and sends Token C only to the fixed AWS route. Token C
is not cached, decoded, logged or returned. AWS remains authoritative for live
membership, mailbox access, object access, revocation, rate limits and audit.

Responses are checked for the contract envelope, operation, workspace and
operation-specific required fields. Redirects are disabled and non-HTTPS API
URLs are rejected except for loopback local testing.
