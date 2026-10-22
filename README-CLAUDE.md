# Neyvro Claude Code Plugin

Neyvro is a Claude Code plugin containing the repository’s canonical `skills/` directory and an optional MCP connection. It does not duplicate or transform the skills: Claude loads the exact same `skills/<name>/SKILL.md` files used by the other agent clients.

## What is included

- 35 current canonical skills in `skills/`.
- The 17 OpenGTM-equivalent workflows.
- 9 Neyvro-exclusive intelligence workflows.
- 9 compatibility documents retained by the existing registry.
- `.claude-plugin/plugin.json` and a Git-installable `.claude-plugin/marketplace.json`.
- A local knowledge-only MCP server already provided by `src/neyvro/mcp_server.py`.
- A remote Streamable HTTP MCP service entry point, usable after Neyvro deploys a real HTTPS endpoint.

The `gtm-automation-with-neyvro` skill is the supported Neyvro execution bridge. The Chronos-named compatibility document does not require or invoke Chronos.

## Mode A — Claude Code plugin

From a Git checkout, install the repository as a marketplace and then install the plugin:

```bash
claude plugin marketplace add https://github.com/neyvro-Distributor/opengtmn-neyvro-.git
claude plugin install neyvro-gtm-intelligence@neyvro
claude plugin list
claude plugin details neyvro-gtm-intelligence@neyvro
```

After installation, restart Claude Code. Skills are discovered from the plugin’s canonical `skills/` directory. Invoke a workflow naturally, for example:

```text
Use Neyvro to find my strongest company opportunities.
Research this prospect using Neyvro.
Prepare an evidence-backed outbound campaign.
Show me who replied to my outreach.
```

For a local checkout, validate directly before installing:

```bash
claude plugin validate .
claude plugin install .
```

Update or remove:

```bash
claude plugin marketplace update neyvro
claude plugin update neyvro-gtm-intelligence@neyvro
claude plugin uninstall neyvro-gtm-intelligence@neyvro
claude plugin marketplace remove neyvro
```

The exact installed version is checked in this repository’s validation log; update the plugin version when publishing a new marketplace release.

## Mode B — Remote Neyvro MCP

The verified Neyvro HTTPS MCP URL is:

```bash
export NEYVRO_MCP_URL="https://opengtmn-neyvro.onrender.com/mcp"
claude mcp add --transport http --scope user neyvro "${NEYVRO_MCP_URL}"
claude mcp login neyvro
claude mcp list
claude mcp get neyvro
```

OAuth authorization is currently unavailable on the deployment: the endpoint is live, but its OAuth issuer and protected-resource metadata are not configured. Do not claim an authenticated connection until the provider is configured. Tokens must never be placed in this repository.

The Neyvro server is tenant-scoped. Research/read tools require the granted read scopes; proposal and external-action workflows require their own authorization and customer approval. A draft is never treated as sent, and no message is silently sent.

If the MCP endpoint is unavailable, continue with knowledge-only skill workflows and state that customer data is unavailable.

## Mode C — Local knowledge MCP

The local server exposes public skill discovery without login or customer records:

```bash
python3 -m pip install -e .
neyvro-mcp-skills
```

Register it with Claude Code using a stdio server. Run this from the repository checkout, replacing the path with the absolute checkout path:

```bash
claude mcp add --transport stdio --scope user neyvro-local \
  --env PYTHONPATH=/absolute/path/to/opengtmn-neyvro-/src \
  -- python3 -m neyvro.mcp_server
claude mcp list
```

Equivalent checked-in examples are available at `examples/claude/neyvro-local.mcp.json` and `examples/claude/neyvro-remote.mcp.json`. The remote example uses Claude Code’s environment-variable expansion and contains no token.

The local server provides `neyvro_list_skills`, `neyvro_get_skill`, and `neyvro_search_skills`. It does not expose private company records or execution tools.

## Permissions and safe use

Use read/research first, then draft, review, and request approval before any external action. Never use `--dangerously-skip-permissions` for Neyvro MCP actions. Do not put bearer tokens, client secrets, API keys, or customer records in `.mcp.json`, marketplace metadata, or plugin files.

## Verification

Run the repository checks:

```bash
claude --version
claude plugin validate .
claude mcp list
python3 scripts/validate_plugin.py
pytest -q
```

The remote connection and OAuth sign-in cannot be verified until a real deployed endpoint and configured identity provider are available. The offline skill path and local MCP path remain testable without them.
