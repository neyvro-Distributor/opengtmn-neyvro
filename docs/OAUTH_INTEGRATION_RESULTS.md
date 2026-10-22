# OAuth integration results

Status: **BLOCKED**.

The remote server supports configured JWT issuer, audience, JWKS, expiry,
issuer, audience, subject, tenant claim, and scope validation. It does not
provide an authorization server, client registration, login UI, PKCE flow, or
token issuance itself. No production identity-provider metadata was available
to verify.

The existing Neyvro backend uses Firebase ID-token validation and issues a
`neyvro_session` cookie. That is not a standards-compatible MCP OAuth issuer
or a trusted service-to-service exchange. Do not expose private tools until an
authorized provider is configured and its issuer/resource metadata is recorded.
