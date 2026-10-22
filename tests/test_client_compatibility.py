import json
from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]
MARKER = "https://__DEPLOYED_NEYVRO_MCP_HOST__/mcp"


def test_cursor_example_is_portable_and_secret_free():
    value = json.loads((ROOT / ".cursor/mcp.json.example").read_text())
    server = value["mcpServers"]["neyvro"]
    assert server == {"url": MARKER}


def test_all_client_json_examples_parse_and_use_the_deployment_marker():
    paths = sorted((ROOT / "examples/client-configurations").glob("*.json"))
    assert paths
    for path in paths:
        value = json.loads(path.read_text())
        assert isinstance(value, dict)
        text = path.read_text()
        assert "Bearer " not in text
        assert MARKER in text


def test_continue_example_is_valid_yaml_and_local_only():
    value = yaml.safe_load((ROOT / "examples/client-configurations/continue-config.yaml").read_text())
    assert value["schema"] == "v1"
    assert value["mcpServers"][0]["command"] == "python3"
    assert value["mcpServers"][0]["args"] == ["-m", "neyvro.mcp_server"]


def test_no_client_specific_skill_fork_exists():
    for relative in (".cursor/skills", ".devin/skills", ".windsurf/skills", ".github/skills"):
        assert not (ROOT / relative).exists(), relative


def test_compatibility_docs_report_conservative_statuses():
    text = (ROOT / "docs/client-compatibility.md").read_text()
    assert "DOCUMENTED_ONLY" in text
    assert "universal" not in text.lower()
