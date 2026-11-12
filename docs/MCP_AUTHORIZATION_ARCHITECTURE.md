# MCP authorization architecture

The gateway has separate identity and authorization boundaries:

1. Token A proves the caller's identity. Firebase Admin revocation/disabled
   checks are mandatory in Firebase mode.
2. A trusted grant evaluator supplies only explicitly granted `intelligence:read`
   and `mail:read` scopes. Tool requests cannot create grants.
3. AWS exchange remains authoritative for NEYVRO account state, workspace
   membership, role, object access and mailbox access.
4. Render signs Token B only after the local identity/grant checks; AWS issues
   opaque Token C for one exact operation and call.

Firebase compatibility and external OAuth are mutually exclusive trust modes.
If both are configured, the server fails closed. Public skill tools remain
available without private customer authorization.
