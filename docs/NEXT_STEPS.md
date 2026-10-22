# Neyvro Next Steps

Run the complete local verification gate with:

```bash
make verify-all
```

The machine-readable result is written to `docs/verification-results.json`.
External credentials, deployment, and provider checks are reported as blockers;
they are never silently skipped as successful.

The repository began as a license-only baseline. The next executable engineering actions are:

1. Deploy the remote MCP service and record its provider-assigned HTTPS URL.
2. Configure the OAuth issuer, PKCE authorization flow, resource metadata, and tenant claims.
3. Add the trusted backend identity exchange and object-level authorization tests.
4. Add shared rate limits, usage/cost budgets, durable audit logs, and idempotency storage.
5. Supply authorized research, CRM, mailbox, and enrichment provider credentials/sandboxes.
6. Run the two-synthetic-tenant workflow and one real external MCP-client read call.

Until provider credentials, identity configuration, and client contracts are available, those integrations must remain marked BLOCKED rather than represented as complete.
