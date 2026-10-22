# Neyvro Next Steps

The repository began as a license-only baseline. The next executable engineering actions are:

1. Confirm the exact 17 OpenGTM skill names and their input/output contracts.
2. Select the MCP SDK/runtime and implement the local server around the existing `TenantStore` interfaces.
3. Define the customer identity model, OAuth issuer, tenant claims, and token verification policy.
4. Add a persistent database adapter with migrations while preserving tenant predicates on every query.
5. Supply authorized research, CRM, mailbox, and enrichment provider contracts before implementing external connectors.
6. Add integration tests for MCP discovery, resources, prompts, and client compatibility.
7. Add Docker/CI configuration after the runtime and deployment target are selected.

Until provider credentials, identity configuration, and client contracts are available, those integrations must remain marked BLOCKED rather than represented as complete.
