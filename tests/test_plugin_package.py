import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_portable_plugin_validator_passes_with_explicit_deployment_blocker():
    result = subprocess.run(
        [sys.executable, "scripts/validate_plugin.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "35 skills" in result.stdout
    assert "BLOCKED" in result.stdout


def test_portable_manifest_and_mcp_config_use_supported_shapes():
    plugin = json.loads((ROOT / "plugin.json").read_text())
    mcp = json.loads((ROOT / "mcp.json").read_text())
    assert plugin["$schema"].endswith("plugin.schema.json")
    assert plugin["extensions"]["com.openai"]["onboardingSkill"].startswith("./")
    server = mcp["mcpServers"]["neyvro"]
    assert server["type"] == "streamable-http"
    assert server["url"].endswith("/mcp")
    assert server["extensions"]["com.openai"]["auth"]["type"] == "oauth"


def test_skill_inventory_has_core_and_exclusive_categories():
    inventory = json.loads((ROOT / "assets/skill-inventory.json").read_text())
    actual = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
    expected = set(inventory["portable_core_skills"]) | set(inventory["neyvro_exclusive_intelligence_skills"]) | set(inventory["legacy_compatibility_skills"])
    assert expected == actual
    assert len(inventory["portable_core_skills"]) == 17
    assert len(inventory["neyvro_exclusive_intelligence_skills"]) == 9


def test_mandatory_release_skill_list_is_complete_and_present():
    mandatory = json.loads((ROOT / "assets/mandatory-skills.json").read_text())
    required = set(mandatory["required_open_gtm_equivalent"]) | set(mandatory["required_neyvro_exclusive"])
    actual = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
    assert len(required) == 26
    assert required <= actual


def test_mcp_registry_metadata_is_explicitly_unpublished_and_secret_free():
    registry = json.loads((ROOT / ".mcp/server.json").read_text())
    assert registry["$schema"].endswith("server.schema.json")
    assert registry["_meta"]["io.modelcontextprotocol.registry/publisher-provided"]["releaseStatus"] == "not-published"
    assert "Bearer " not in (ROOT / ".mcp/server.json").read_text()


def test_claude_plugin_manifests_and_examples_are_present():
    manifest = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
    marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
    local_mcp = json.loads((ROOT / "examples/claude/neyvro-local.mcp.json").read_text())
    remote_mcp = json.loads((ROOT / "examples/claude/neyvro-remote.mcp.json").read_text())
    assert manifest["name"] == "neyvro-gtm-intelligence"
    assert manifest["version"] == marketplace["plugins"][0].get("version", manifest["version"])
    assert marketplace["plugins"][0]["source"] == "."
    assert local_mcp["mcpServers"]["neyvro-local"]["command"] == "python3"
    assert remote_mcp["mcpServers"]["neyvro"]["url"] == "${NEYVRO_MCP_URL}"
