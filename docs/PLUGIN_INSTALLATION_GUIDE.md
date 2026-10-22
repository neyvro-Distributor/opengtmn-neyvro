# Neyvro plugin installation guide

## Portable package

The canonical package contains the root `plugin.json`, `mcp.json`, `skills/`,
`assets/`, and MIT license. It uses the live endpoint
`https://opengtmn-neyvro.onrender.com/mcp` and contains no credentials.

Validate locally:

```bash
python3 scripts/validate_plugin.py
python3 scripts/validate_release.py
pytest -q
```

## Codex

```bash
codex mcp add neyvro --url https://opengtmn-neyvro.onrender.com/mcp
codex mcp list
```

The server is registered in the current environment. OAuth login and private
tool calls remain blocked until the deployment advertises a real issuer.

## Claude Code

```bash
claude mcp add --transport http --scope user neyvro https://opengtmn-neyvro.onrender.com/mcp
claude mcp list
claude mcp get neyvro
```

Install the repository plugin from its Git marketplace only after reviewing the
plugin manifest. The plugin exposes the same canonical `skills/` directory.

## Cursor and other clients

Use `.cursor/mcp.json.example` or the files under
`examples/client-configurations/`. These files contain the live URL and no
secrets. Client UI authentication is not claimed as complete while OAuth is
blocked.

## Offline mode

For public knowledge skills without login:

```bash
python3 -m pip install -e .
neyvro-mcp-skills
```

Offline mode never exposes private company records or execution tools.
