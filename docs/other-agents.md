# Other MCP-compatible agents

These instructions use the same canonical root skills. If a client cannot
discover the root directory, install or link the canonical directory using the
client's documented mechanism; do not author a fork.

## Windsurf / Devin Cascade

Cascade reads `mcp_config.json` from the documented user configuration path
(`~/.config/devin/mcp_config.json` on macOS/Linux) and supports stdio,
Streamable HTTP, SSE, and OAuth. A valid remote entry is shown in
`examples/client-configurations/windsurf-mcp_config.json`. Add the deployed
URL and authenticate through the client; do not add a token to the file.

For skills, use the workspace `.devin/skills/` directory or the documented
global skills directory. A release process may copy the canonical `skills/`
contents there, but the repository root remains the source of truth.

## Cline

Cline stores MCP settings in `~/.cline/data/settings/cline_mcp_settings.json`
and supports a `streamableHttp` remote transport. Use the example in
`examples/client-configurations/cline-mcp-settings.json`, then use Cline's MCP
UI or `cline mcp` to authenticate. Cline's `autoApprove` list should remain
empty for Neyvro until a customer explicitly approves an exact action.

The local stdio MCP can be configured instead when only public skills are
needed. Cline's plugin/skill discovery varies by host editor, so use the
canonical package or the local MCP rather than assuming a plugin manifest is
loaded.

## Continue

Continue supports MCP entries in `~/.continue/config.yaml`. The checked-in
example uses the local stdio server, which is portable and does not need an
endpoint or credentials. Continue also documents HTTP request options, but
this repository does not claim a tested OAuth flow for Continue.

## Zed

Add Neyvro from **Settings → AI → MCP Servers** or use Zed's documented MCP
configuration. Zed supports MCP tools and prompts; resource support is not
claimed here. If the server has no Authorization header, Zed can start its
standard MCP OAuth flow. Leave tool permissions at review-required defaults.

## VS Code GitHub Copilot Agent mode

For a workspace, `.mcp.json` uses the portable `mcpServers` shape. VS Code's
`.vscode/mcp.json` uses its own `servers` shape, so use the official schema and
the client UI if you choose that file. The portable example is
`examples/client-configurations/vscode-workspace.mcp.json`.

Agent Skills are documented in `.github/skills/`, `.claude/skills/`, and
`.agents/skills/` (with user-level equivalents). If a workspace needs one of
those paths, generate a synchronized installation from the canonical root;
never hand-edit a second version.

## Gemini CLI

Gemini supports skills installation/linking and MCP server management. The
documented commands are:

```sh
gemini skills link /absolute/path/to/opengtmn-neyvro-/skills
gemini mcp add <server-name> https://__DEPLOYED_NEYVRO_MCP_HOST__/mcp --transport http
gemini mcp list
```

The command above intentionally uses a placeholder and must be changed to the
real deployed URL before use. The checked-in JSON example uses `httpUrl`, which
selects Streamable HTTP; `/mcp auth <server-name>` starts the client's OAuth flow
when the deployment advertises OAuth. (The displayed command name is written
without an underscore because Gemini reserves underscores in server aliases.)

## Generic MCP clients

Use the root `mcp.json` when the client implements the Agent Plugin format. If
it only accepts MCP configuration, translate the server's HTTPS URL into its
documented Streamable HTTP field. Check `tools/list`, `resources/list`, and
`prompts/list` separately: support for one surface does not imply support for
the others. Clients without native skills can run `neyvro-mcp-skills` over
stdio.

## Status

Cursor, Windsurf, Cline, Continue, Zed, VS Code, and Gemini are
`DOCUMENTED_ONLY` in this repository. Their official documentation was
reviewed, but this workspace has no authenticated deployed Neyvro endpoint and
no headless end-to-end client sessions for them.
