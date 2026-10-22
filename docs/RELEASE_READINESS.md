# Release readiness

## Local gates

- Mandatory skills: PASS (26 required, 35 packaged)
- Repository tests: PASS (141)
- Backend targeted tests: PASS (225)
- Plugin validation: PASS
- Render Blueprint validation: PASS
- `git diff --check`: PASS

## Production gates

- HTTPS deployment: BLOCKED
- OAuth/PKCE issuer: BLOCKED
- Trusted backend identity exchange: BLOCKED
- Two-tenant live isolation test: NOT TESTED
- Authenticated Codex invocation: NOT TESTED
- Authenticated ChatGPT invocation: NOT TESTED

Release status: **NO-GO** until every production gate is verified with real,
authorized infrastructure.
