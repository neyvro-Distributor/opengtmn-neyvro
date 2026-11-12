# MCP authorization security tests

The local suite has **167 passing tests** after this change. Added coverage
includes:

- Firebase scope claims ignored without a trusted grant;
- explicit test-grant expiry/project restrictions;
- Firebase `intelligence:read` and `mail:read` separation;
- issuer-qualified OAuth identity binding and unlinked-subject denial;
- Firebase/external mode configuration conflict;
- Token B scope-elevation rejection;
- original missing-scope behavior reproduced and safely preserved.

Tests use generated in-memory keys and synthetic identities. They are not real
Firebase or hosted OAuth E2E. No JWT values or credentials are persisted.
