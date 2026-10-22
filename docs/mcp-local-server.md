# Local Neyvro Skills MCP server

The local MCP server is a knowledge boundary, separate from Neyvro’s customer-data and execution services. It reads the fixed repository `skills/` directory at startup and registers every valid `SKILL.md` exactly once.

## Security boundary

- Only public skill metadata and Markdown are exposed.
- Customer records, credentials, provider connections, and execution services are not exposed.
- Resource URIs are allowlisted as `neyvro://skills/<exact-skill-name>`.
- Tool requests load exact registry identifiers; partial names and filesystem paths are rejected.
- Resource content is bounded to 256 KiB.
- The server never accepts a caller-supplied root directory.
- stdout is reserved for MCP protocol messages; diagnostics use stderr.

## Protocol surface

The official Python MCP SDK’s `FastMCP` stdio transport provides:

- `neyvro_list_skills` for bounded metadata discovery;
- `neyvro_get_skill` for exact metadata and original content;
- `neyvro_search_skills` for deterministic metadata/content search;
- one resource at `neyvro://skills/<skill-name>` per canonical skill;
- one prompt per skill with a derived title and the skill activation description.

The local server does not call `neyvro_get_capabilities` or any customer execution contract. Use the separate Neyvro-native automation bridge when a workflow needs connected data or an approved action.

## Verification

`tests/test_mcp_server.py` launches `python -m neyvro.mcp_server` through the official SDK `ClientSession` and checks tools/list, tools/call, resources/list, resources/read, prompts/list, prompts/get, exact content, 35 registrations, and unknown skill handling.
