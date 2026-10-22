# Neyvro Agent Plugin

The package follows the current Agent Plugins 1.0.0 layout: root `plugin.json`, root `mcp.json`, root `skills/`, optional `assets/`, and an optional `.codex-plugin/plugin.json` compatibility fallback. OpenAI-specific presentation and onboarding metadata are under `extensions.com.openai`; MCP authentication is declared under the server entry in `mcp.json`.

## Current package contents

- 17 OpenGTM-equivalent Neyvro skills.
- 9 Neyvro-exclusive digital-twin, evidence, predictive-intelligence, buyer, investigation, and attribution skills.
- 9 legacy compatibility documents retained in the current canonical library, including the Chronos-named document. The supported execution bridge is `gtm-automation-with-neyvro`; no Chronos account or API is required.
- Authenticated Streamable HTTP MCP configuration using OAuth DCR metadata.
- Codex compatibility overlay and explicit local skill installer.

## Endpoint status

No deployed Neyvro remote endpoint was found in the workspace. Therefore `mcp.json` contains the deliberately obvious marker `https://__DEPLOYED_NEYVRO_MCP_HOST__/mcp`; it is not a production address. Replace it with the real provider-assigned HTTPS URL after deployment, then run the validator again.

The remote server already supports `/mcp` and `/health` when run locally, but its customer-data adapter remains disabled until the trusted OAuth-to-backend tenant exchange, durable audit/usage controls, and backend contracts described in [remote-mcp-readiness.md](remote-mcp-readiness.md) are deployed.

## Skill behavior

Knowledge-only workflows work without a Neyvro login. Research and customer-data workflows require the remote MCP connection and granted scopes. Drafts remain drafts; proposals require explicit approval; sending, publishing, and other external actions remain separately gated by the remote backend.

## Validation

```bash
python3 scripts/validate_plugin.py
neyvro-skills validate
pytest -q
```

From a checkout where the package is not installed, use `python3 -m pip install -e .` first.
