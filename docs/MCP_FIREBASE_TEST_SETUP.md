# Firebase test setup for genuine MCP E2E

This checklist is required before claiming real E2E. It is intentionally
manual: the repository does not create cloud projects or retrieve credentials.

1. Create or select a dedicated nonproduction Firebase project whose ID is
   explicitly allowlisted by the gateway. A name containing `test` is not
   sufficient by itself.
2. Confirm the project has no production service account, database, customer
   identity, or signing key. Keep Admin credentials on the gateway host only.
3. Create dedicated verified-email users A and B for separate synthetic
   workspaces. Record their actual Firebase UIDs; never use email as identity.
4. Configure exact server-managed grants for each UID, including supported
   scope, expiry, revocation state, nonproduction environment, and trusted
   administrative origin. Firebase `scope`/`scp` claims are not grants.
5. Configure a controlled user C only if `mail:read` is explicitly approved;
   otherwise use C for a denied-mail test. Do not invent mailbox privileges.
6. Ensure matching synthetic AWS identity and workspace membership records
   exist in the isolated `_mcp_dev` database. Seed records through the AWS
   developer's approved harness and do not mutate production data.
7. Obtain Token A using an approved Firebase client flow. Keep it in memory or
   a protected local secret store, pass it as `NEYVRO_E2E_TOKEN_A`, and never
   print it or place it in JSON/Markdown reports.
8. Verify Firebase Admin revocation/disabled-user checks on the gateway before
   running positive calls.

If any item is unavailable, report `REAL_E2E=BLOCKED`. A fabricated JWT,
ordinary ungranted Firebase token, or mocked handler result is not evidence of
genuine identity or AWS authorization.
