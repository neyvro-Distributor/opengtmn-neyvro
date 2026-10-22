# E2E next steps

1. Deploy `neyvro-mcp-remote` to authorized Neyvro hosting and record its real
   HTTPS `/mcp` URL.
2. Configure OAuth authorization-code + PKCE, protected-resource metadata,
   issuer/audience/JWKS, and tenant claims.
3. Configure the trusted backend identity exchange and a synthetic two-tenant
   staging dataset.
4. Run the external MCP Inspector and real Codex read-only session.
5. Connect ChatGPT through its current custom MCP flow and run the redacted
   scenarios in `CHATGPT_REAL_CONNECTION_RESULTS.md`.
6. Add live Gmail/Microsoft/CRM/enrichment sandbox tests before enabling any
   external action.
7. Rerun `make verify-all` and update statuses only from observed evidence.
