# MCP-to-backend authentication bridge

Status: **BLOCKED / DESIGN CONFIRMED**.

The remote gateway never forwards the customer's bearer token to the backend.
The intended boundary is:

1. Verify the external OAuth token at the MCP gateway.
2. Resolve subject, workspace, audience, expiry, and scopes.
3. Exchange that principal for a short-lived backend assertion addressed to the
   Neyvro API.
4. Revalidate workspace membership and object authorization in the backend.
5. Audit both allowed and denied calls.

The existing backend does not yet expose step 3. A static service token plus a
caller-provided workspace header is insufficient and is therefore not enabled
as production readiness. No administrative bypass is permitted.
