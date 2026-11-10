# MCP authorization matrix

## Token responsibilities

| Token | Issuer | Receiver | Purpose | Lifetime | Gateway handling |
|---|---|---|---|---|---|
| Token A | Google Firebase | Render MCP | Proves Firebase identity | Firebase-defined, normally 1 hour | Verify RS256, issuer, audience, `exp`, `iat`, `auth_time`, `sub`, revocation and disabled state |
| Token B | Render | AWS exchange | Vouches for verified identity and requested operation | ≤60 seconds, single-use | Fresh ES256 assertion per invocation; never cache or log |
| Token C | NEYVRO API | AWS MCP route | Authorizes the exact user/workspace/operation/scope | 60 seconds, one tool call | Treat as opaque; never decode for authorization, return, or log |

## Current operation policy

| MCP tool | Operation | Scope | Workspace source | Side effect | Availability |
|---|---|---|---|---|---|
| `neyvro_search_companies` | `companies.search` | `intelligence:read` | Optional lowercase UUID request in Token B; AWS membership is authoritative | Read-only; no credits | Callable only when bridge flag and credentials are valid |
| Other 55 private tools | None contracted | Default deny | No trusted workspace authorization | Unknown, potentially unsafe | Disabled and not registered |

Firebase identity and workspace grants are deliberately separate. Render does
not add workspace claims to Firebase tokens and does not treat an incoming
workspace claim as membership proof. A 409 `choose_workspace` response is
returned as a safe workspace-selection result; the next invocation must create
a new Token B.

## AWS error handling

The adapter maps contract errors without returning backend messages or tokens:

- `401`: unauthorized; do not retry the same assertion.
- `403`: forbidden; stop for membership, role, account, or scope failures.
- `409 choose_workspace`: return only validated workspace id/name/role choices.
- `429`: rate-limited.
- `422`: invalid request.
- `503`, timeout, malformed response: backend unavailable.

## External MCP OAuth

Firebase is a first-party compatibility mode only. External MCP clients still
require a standards-compliant OAuth authorization server, resource audience
validation, scopes, and PKCE. OAuth configuration does not substitute for AWS
workspace authorization.
