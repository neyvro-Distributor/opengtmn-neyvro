# MCP identity binding

External OAuth `iss` and `sub` values are not assumed to be Firebase UIDs.
Private access requires an explicit issuer-qualified binding to the canonical
Firebase UID expected by the AWS bridge. Bindings are loaded from the protected
`NEYVRO_MCP_OAUTH_IDENTITY_BINDINGS_JSON` setting, keyed by issuer and subject,
and may carry expiry/revocation state.

Bindings never match by email, accept client-provided UID overrides, or infer
an account from a workspace claim. Unknown, expired, revoked or ambiguous
bindings are rejected before Token B signing. AWS still performs the live
account and workspace authorization checks.
