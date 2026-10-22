# OAuth verification

Status: **BLOCKED**.

The MCP boundary has configured JWT verification support for issuer, audience,
JWKS, expiry, subject, tenant, and scopes. No production identity provider,
authorization endpoint, token endpoint, PKCE client registration, or issuer
metadata is configured.

The Neyvro backend currently validates Firebase identity and creates a session
cookie. Gmail or Microsoft mailbox OAuth is not a substitute for the MCP
customer authorization server. Human action required: provision or authorize
a standards-compatible OAuth provider and provide its non-secret issuer,
resource, authorization, token, and JWKS metadata.
