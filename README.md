# Neyvro Agent Skills & MCP

Portable GTM, company-intelligence, and evidence-grounded workflow skills for
Codex, Claude Code, Cursor, and compatible MCP clients.

Neyvro provides one canonical `skills/` library and one remote MCP boundary.
Client-specific files are installation adapters; they do not fork skill content
or business logic.

## Release status

The public transport is live and independently verified:

- MCP endpoint: `https://opengtmn-neyvro.onrender.com/mcp`
- Health: HTTP 200
- MCP protocol: `2025-06-18` initialization verified
- Tools: 56 discoverable contracts
- Skill resources: 35 discoverable and readable
- Prompts: 35 discoverable
- Skill gate: 26 mandatory skills; 35 packaged skills
- Repository tests: 141 passing

Customer-data access is currently fail-closed. Production OAuth/PKCE, the
MCP-to-backend delegated identity bridge, and authenticated tenant-isolation
tests are not yet configured. Tool discovery is not authorization and does not
indicate that private records are available.

## What is included

- 35 canonical Agent Skills with metadata-based discovery and on-demand loading.
- Local knowledge-only MCP server using the official Python MCP SDK and stdio.
- Remote Streamable HTTP MCP boundary with scoped tool contracts and approval
  metadata.
- Portable Agent Plugin files: `plugin.json`, `mcp.json`, `skills/`, and
  `assets/`.
- Claude Code, Cursor, Codex, VS Code, Gemini, Windsurf, and Cline examples.
- Explicit safety boundaries for read, research, draft, propose, approve,
  execute, publish, and verify workflows.

## Local MCP server

The local server exposes the public skill library only. It does not connect to customer data, require a Neyvro login, or expose execution tools.

Install the package in an environment with Python 3.11 or newer:

```bash
python3 -m pip install -e .
```

Start the stdio MCP server:

```bash
neyvro-mcp-skills
```

The server uses the official Python MCP SDK and stdio transport. Protocol traffic is written to stdout; diagnostics go to stderr.

Available tools:

- `neyvro_list_skills`
- `neyvro_get_skill`
- `neyvro_search_skills`

Resources use `neyvro://skills/<skill-name>`. Each skill is also registered as a prompt using its title and activation description.

### Sample configuration

For MCP clients that accept a JSON server configuration:

```json
{
  "mcpServers": {
    "neyvro-local-skills": {
      "command": "/absolute/path/to/venv/bin/neyvro-mcp-skills",
      "args": []
    }
  }
}
```

Alternatively use the repository checkout directly:

```json
{
  "mcpServers": {
    "neyvro-local-skills": {
      "command": "/usr/bin/env",
      "args": ["python3", "-m", "neyvro.mcp_server"],
      "cwd": "/absolute/path/to/opengtmn-neyvro-",
      "env": {"PYTHONPATH": "/absolute/path/to/opengtmn-neyvro-/src"}
    }
  }
}
```

Use the first form after installation. Do not pass arbitrary skill roots or filesystem paths to the server.

## Remote MCP boundary

The separate `neyvro-mcp-remote` command exposes tenant-scoped customer-data contracts over official Streamable HTTP at `/mcp`. It requires configured OAuth issuer/audience/JWKS and a server-side backend credential, never forwards inbound bearer tokens, and fails closed when a capability is unavailable. Provider-assigned HTTPS hosting is sufficient; no custom domain is required.

```bash
neyvro-mcp-remote
```

See [docs/remote-mcp-readiness.md](docs/remote-mcp-readiness.md) for the configuration, security boundary, tool readiness matrix, and blockers. Tool registration is discovery only: a listed tool is not evidence that the underlying backend capability is enabled.

## Portable Agent Plugin

This repository is also a portable Agent Plugins package. It contains the root `plugin.json`, `mcp.json`, `.codex-plugin/plugin.json` compatibility overlay, `assets/`, and all 35 current skill directories. The package includes the 17 OpenGTM-equivalent workflows, 9 Neyvro-exclusive intelligence workflows, and 9 legacy compatibility skill documents; see `assets/skill-inventory.json` for the explicit inventory.

The verified remote MCP URL is:

```text
https://opengtmn-neyvro.onrender.com/mcp
```

The transport and public skill surfaces are live. Customer-data tools remain
disabled until production OAuth and the backend trust bridge are configured.

### Codex local skills

Install the Markdown skills into a supported Codex skills directory by passing an explicit target:

```bash
./scripts/install-codex-skills.sh ~/.codex/skills/neyvro
```

The script copies only `SKILL.md` files and does not overwrite the plugin or customer data. The portable package remains the source of truth.

### Codex MCP connection

Configure the current Codex CLI:

```bash
codex mcp add neyvro --url "https://opengtmn-neyvro.onrender.com/mcp"
codex mcp list
```

The server is registered in the verified Codex environment. OAuth login and
private-data calls remain blocked until a real authorization provider is
configured. Never put client secrets or bearer tokens in `mcp.json`.

### ChatGPT and plugin installation

For local testing, add this repository or a copied package to a personal/repo
plugin marketplace using the current Agent Plugins format. For a custom remote
MCP connection, use ChatGPT → Add custom MCP server and enter the deployed
`/mcp` URL. OAuth and private-data invocation remain blocked until the provider
is configured. Public marketplace publication is not claimed.

Public distribution requires the OpenAI plugin submission/review process and a deployed HTTPS endpoint. This repository does not claim marketplace publication or approval.

### Example requests

- “Use Neyvro to find my strongest company opportunities.”
- “Research this prospect using Neyvro.”
- “Prepare an evidence-backed outbound campaign.”
- “Show me who replied to my outreach.”

Run `python3 scripts/validate_plugin.py` to validate the package structure,
skill inventory, safe paths, OAuth declaration, and configured endpoint.

For release and security evidence, see [docs/PRODUCTION_CLIENT_RELEASE.md](docs/PRODUCTION_CLIENT_RELEASE.md), [docs/OAUTH_CLIENT_COMPATIBILITY.md](docs/OAUTH_CLIENT_COMPATIBILITY.md), and [docs/e2e/CLIENT_COMPATIBILITY_MATRIX.md](docs/e2e/CLIENT_COMPATIBILITY_MATRIX.md). The current assessment is NO-GO for private customer-data access because no OAuth issuer or backend trust bridge is configured.

## Validation and tests

```bash
neyvro-skills validate
neyvro-skills build
pytest -q
```

The MCP protocol test starts the real local subprocess with the official MCP client and verifies initialization, tool listing/calls, resource listing/reading, prompt listing/retrieval, exact content, argument validation, and unknown skill handling.
