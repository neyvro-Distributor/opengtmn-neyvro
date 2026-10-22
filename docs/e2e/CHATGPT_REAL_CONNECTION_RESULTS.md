# ChatGPT real connection results

Status: BLOCKED / NOT_TESTED.

No deployed HTTPS MCP endpoint was available and no authenticated custom MCP
connection was created in the ChatGPT UI. Therefore no claim is made for native
ChatGPT tool discovery, OAuth consent, tool invocation, tenant isolation, or
conversation behavior.

Human-assisted verification after deployment:

1. Open ChatGPT's supported custom MCP/connectors interface.
2. Add the actual Neyvro HTTPS `/mcp` URL.
3. Complete the displayed OAuth login and consent flow.
4. Start a new conversation and ask for Neyvro capabilities.
5. Confirm a read-only tool call and inspect the returned tenant-scoped data.
6. Test an unauthorized send and cross-tenant request; both must be rejected.

The exact UI and callback URL must come from the current ChatGPT interface; no
callback or permission was guessed here.
