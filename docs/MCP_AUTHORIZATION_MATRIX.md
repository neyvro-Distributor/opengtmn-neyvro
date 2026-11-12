# MCP authorization matrix

| Token | Issuer → receiver | Purpose |
|---|---|---|
| A | Firebase → Render | Verified caller identity and granted scopes |
| B | Render → AWS exchange | Fresh exact operation/scope assertion, ≤60 seconds, single-use JTI |
| C | AWS → Render route | AWS live authorization for one user/workspace/operation and one call |

Render never forwards Token A, fabricates workspace membership, or exposes
Token C. A requested workspace is only a selection request; AWS checks
membership and mailbox-level access on every call. Unsupported tools are not
registered as callable tools. Cross-workspace, revoked-membership, wrong
operation, missing-scope, malformed-input and malformed-response cases fail
closed without revealing bearer material.
