# Remote endpoint results

Status: LIVE / PARTIAL.

Render inspection found the existing Neyvro service `opengtmn-neyvro` in the
authorized workspace. It was repaired in place; no duplicate service or
database was created.

The live service is Docker-based and runs commit `db8bb58d…` at
`https://opengtmn-neyvro.onrender.com`. Render built the image remotely.

The live MCP endpoint is:

`https://opengtmn-neyvro.onrender.com/mcp`

External TLS, `/health`, MCP initialize, `tools/list`, `resources/list/read`,
`prompts/list`, and safe unauthenticated tool rejection passed. Live backend
customer-data response, OAuth, and authenticated client calls remain blocked.

Required next action: configure production OAuth and the backend trust bridge,
then rerun authenticated data tests from Codex and ChatGPT.
