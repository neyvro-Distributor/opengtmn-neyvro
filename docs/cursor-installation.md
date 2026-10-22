# Cursor installation

Neyvro uses the portable Agent Plugin layout as its canonical package: the root
`plugin.json`, `mcp.json`, and `skills/` directory. Cursor supports that layout,
so this repository does not maintain a second copy of the skills or a
Cursor-only plugin manifest.

## Local user installation

Cursor's documented local-plugin flow discovers a package under
`~/.cursor/plugins/local`. Copy this repository (or a release archive) there,
then restart Cursor or run **Developer: Reload Window**:

```sh
mkdir -p "$HOME/.cursor/plugins/local"
cp -R /absolute/path/to/opengtmn-neyvro- \
  "$HOME/.cursor/plugins/local/neyvro-gtm-intelligence"
```

Use Cursor's Customize/Plugins UI to enable the plugin for the user scope.
For project scope, install the same package through Cursor's plugin UI and
choose the project scope. Do not create another `skills/` tree in the project.

To update a local copy, replace only the package directory with a newer release
and reload Cursor. To uninstall it, remove the explicit package directory:

```sh
rm -rf "$HOME/.cursor/plugins/local/neyvro-gtm-intelligence"
```

## Remote Neyvro MCP

The root `mcp.json` is the portable configuration. Cursor can also add a
Streamable HTTP server from its MCP/Tools settings. Use the deployed `/mcp`
endpoint and complete interactive OAuth when Cursor presents it. No token is
stored in this repository.

`.cursor/mcp.json.example` is a setup example only. Replace
`https://__DEPLOYED_NEYVRO_MCP_HOST__/mcp` only after Neyvro has a real HTTPS
deployment; the repository currently has no deployed endpoint.

## Local knowledge-only MCP

For offline use, install the package in editable mode and add this command as a
stdio MCP server in Cursor's MCP UI:

```sh
python3 -m pip install -e .
```

Command: `neyvro-mcp-skills` (or `python3 -m neyvro.mcp_server` with the
repository's `src` on `PYTHONPATH`). This server exposes public skill content
only and does not require a Neyvro login. It must not be used as a substitute
for the authenticated remote execution service.

Knowledge skills can read and plan while disconnected. Customer data,
enrichment, sending, publishing, and other external actions remain unavailable
or approval-gated. A draft is never a sent message.

## Verification

Check that the plugin appears in Cursor's plugin UI, that the Neyvro server
appears under MCP, and that `neyvro_list_skills` is discoverable. If OAuth is
not configured on the deployment, use the local knowledge MCP instead and mark
remote execution unavailable.

Status in this repository: `DOCUMENTED_ONLY` for Cursor. The installed Cursor
binary was detected, but a GUI plugin installation and authenticated remote
call were not run in this headless workspace.
