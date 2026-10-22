# Architecture verification

The repository preserves a layered boundary:

1. `skills/` contains the canonical portable instructions.
2. `src/neyvro/skill_library.py` performs deterministic registry, loading,
   search, validation, and artifact generation.
3. `src/neyvro/mcp_server.py` is a knowledge-only stdio MCP server.
4. `src/neyvro/remote_mcp.py` is a separate Streamable HTTP boundary with
   OAuth/scope/tenant/readiness gates.
5. Existing domain modules provide bounded local contracts and do not replace
   the Neyvro backend.

The remote server now exposes 56 explicit tool contracts plus public skill
resources/prompts. Tool discovery is not capability verification: handlers
return readiness states and the backend adapter fails closed without a trusted
server credential.

Architectural findings:

- No Chronos `geo_*` dependency is used.
- No private customer data is exposed by the local server.
- Incoming MCP bearer tokens are not forwarded to the backend.
- Customer-data execution, publishing, and sending remain disabled until the
  backend identity, approval, provider, and idempotency contracts exist.
- A deployed production system still needs shared rate limits, usage budgets,
  durable audit storage, and DNS-rebinding-safe egress controls.
