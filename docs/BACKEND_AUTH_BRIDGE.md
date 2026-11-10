# MCP-to-backend authentication bridge

Status: **MCP RESOURCE SERVER IMPLEMENTED / BACKEND BRIDGE BLOCKED**.

The remote gateway never forwards the customer's bearer token to the backend.
The intended boundary is:

1. Verify the external OAuth token at the MCP gateway.
2. Resolve subject, workspace, audience, expiry, and scopes.
3. Exchange that principal for a short-lived backend assertion addressed to the
   Neyvro API.
4. Revalidate workspace membership and object authorization in the backend.
5. Audit both allowed and denied calls.

The MCP resource server now validates an explicitly configured HTTPS issuer,
JWKS, audience, expiry, issued-at, subject, and RS256 signature. If a trusted
workspace claim is present it is carried in request-scoped auth context; a
Firebase `sub` or email is never treated as a workspace. Configuration alone
reports `CONFIGURED`; only a real verified token changes authentication
readiness to `VERIFIED`.

The existing backend does not yet expose step 3. A static service token plus a
caller-provided workspace header is insufficient and is therefore deliberately
not enabled as a production adapter. No administrative bypass is permitted.

## AWS implementation contract (pending the backend owner)

The backend owner must expose a token-exchange or delegated-assertion endpoint
that accepts a gateway-authenticated principal and returns a short-lived
assertion addressed to the AWS API. The assertion must contain a stable subject,
the verified workspace/tenant, granted scopes, `iat`, `exp` (short lifetime), a
unique `jti`, and an audience identifying the AWS API. AWS must verify the
signature against a pinned issuer/JWKS, validate issuer/audience/time claims,
perform its own workspace membership and object-level authorization checks, and
reject missing or mismatched tenant context. The gateway must send that
assertion only over HTTPS and must never forward the original MCP bearer token.

The bridge must also return an auditable exchange identifier and support key
rotation/replay protection. Write, approval, and campaign-changing operations
remain disabled until this contract and its negative authorization tests pass.
