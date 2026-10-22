# Neyvro Agent Skills

Portable, knowledge-only Agent Skills for Codex, Claude Code, Cursor, and MCP-compatible clients.

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

## Remote customer-data MCP boundary

The separate `neyvro-mcp-remote` command exposes tenant-scoped customer-data contracts over official Streamable HTTP at `/mcp`. It requires configured OAuth issuer/audience/JWKS and a server-side backend credential, never forwards inbound bearer tokens, and fails closed when a capability is unavailable. Provider-assigned HTTPS hosting is sufficient; no custom domain is required.

```bash
neyvro-mcp-remote
```

See [docs/remote-mcp-readiness.md](docs/remote-mcp-readiness.md) for the configuration, security boundary, tool readiness matrix, and blockers. Tool registration is discovery only: a listed tool is not evidence that the underlying backend capability is enabled.

## Portable Agent Plugin

This repository is also a portable Agent Plugins package. It contains the root `plugin.json`, `mcp.json`, `.codex-plugin/plugin.json` compatibility overlay, `assets/`, and all 35 current skill directories. The package includes the 17 OpenGTM-equivalent workflows, 9 Neyvro-exclusive intelligence workflows, and 9 legacy compatibility skill documents; see `assets/skill-inventory.json` for the explicit inventory.

The remote MCP URL is intentionally a deployment marker because no deployed Neyvro HTTPS endpoint is available in this repository. Replace the `url` in `mcp.json` only after deploying the remote server. Do not publish or install the package as a connected plugin while that marker remains.

### Codex local skills

Install the Markdown skills into a supported Codex skills directory by passing an explicit target:

```bash
./scripts/install-codex-skills.sh ~/.codex/skills/neyvro
```

The script copies only `SKILL.md` files and does not overwrite the plugin or customer data. The portable package remains the source of truth.

### Codex MCP connection

After a real HTTPS endpoint is deployed, configure the current Codex CLI:

```bash
codex mcp add neyvro --url "https://<deployed-host>/mcp" \
  --oauth-client-registration dcr \
  --oauth-resource "neyvro-mcp"
codex mcp login neyvro --oauth-client-registration dcr --scopes intelligence:read
codex mcp list
```

Use the actual host and resource values supplied by the Neyvro deployment. Do not put client secrets or bearer tokens in `mcp.json`. If the provider uses a pre-registered client, use `--oauth-client-id` during `codex mcp add` instead of DCR.

### ChatGPT and plugin installation

For local testing, add this repository or a copied package to a personal/repo plugin marketplace using the current Agent Plugins marketplace format, then install it in the ChatGPT desktop app. The portable package uses the root manifest; `.codex-plugin/plugin.json` is only a compatibility fallback. For a custom remote MCP connection, use ChatGPT Plugins → Add custom MCP server, enter the deployed `/mcp` URL, review the risk warning, and complete Neyvro OAuth authorization. Verify the connection in a new conversation and test the packaged onboarding workflow.

Public distribution requires the OpenAI plugin submission/review process and a deployed HTTPS endpoint. This repository does not claim marketplace publication or approval.

### Example requests

- “Use Neyvro to find my strongest company opportunities.”
- “Research this prospect using Neyvro.”
- “Prepare an evidence-backed outbound campaign.”
- “Show me who replied to my outreach.”

Run `python3 scripts/validate_plugin.py` to validate the package structure, skill inventory, safe paths, OAuth declaration, and deployment-marker status.

For the release gate and security/readiness reports, run `python3 scripts/validate_release.py` and see [docs/release-readiness.md](docs/release-readiness.md). The current assessment is NO-GO for public customer-data access because no remote HTTPS deployment or OAuth issuer is configured.

## Validation and tests

```bash
neyvro-skills validate
neyvro-skills build
pytest -q
```

The MCP protocol test starts the real local subprocess with the official MCP client and verifies initialization, tool listing/calls, resource listing/reading, prompt listing/retrieval, exact content, argument validation, and unknown skill handling.
