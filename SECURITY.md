# Security policy

## Supported versions

Only the current repository revision is supported while the package is in
pre-release validation. The public release status is documented in
`docs/release-readiness.md`.

## Reporting a vulnerability

Do not disclose tenant data, credentials, tokens, or exploit details in a
public issue. Contact the Neyvro security owner through the repository's
private GitHub security reporting channel once the repository is public. Until
that channel is enabled, report privately to the repository maintainer and
include a minimal reproduction without production data.

## Security boundaries

- The local MCP server exposes public skill documents only.
- The remote server requires OAuth claims, scopes, and tenant matching.
- Drafts and proposals are not sends or publications.
- The remote endpoint is not release-ready while its deployment marker and
  missing backend identity exchange remain unresolved.
