# Remote endpoint results

Status: BLOCKED.

Render inspection on 2026-10-23 found no deployed Neyvro web service in the
authorized workspace. The workspace contains an unrelated temporary
`neyvro-db` Postgres resource, but no Neyvro MCP/API service. It was not used.

The checked-in `render.yaml` Blueprint is syntactically valid and plans one
Docker web service named `mcp-gateway`, but it has not been created or deployed.
The local Docker build could not run because the Docker daemon is unavailable.
The source is also not present on the origin default branch; a broad direct
push was not performed because it would include unrelated uncommitted work.

No actual public HTTPS endpoint was found in repository configuration or the
available hosting context. `mcp.json` intentionally contains:

`https://__DEPLOYED_NEYVRO_MCP_HOST__/mcp`

This marker is not a test endpoint. Consequently the following checks are
NOT_TESTED: public TLS, external `/mcp` connectivity, proxy streaming behavior,
public tool discovery, live backend response, public rate limiting, and
production monitoring.

Local-only health evidence is recorded in
`docs/e2e/MCP_PROTOCOL_RESULTS.md`. Required deployment action: authorize a
scoped release of this repository, create the validated Blueprint on Render,
configure the production OAuth and backend identity bridge, record the
provider-assigned HTTPS URL, then rerun this report from outside the
application process.
