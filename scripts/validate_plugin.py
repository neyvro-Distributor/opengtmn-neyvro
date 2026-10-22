"""Validate the portable Neyvro Agent Plugin package without network access."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDER = "https://__DEPLOYED_NEYVRO_MCP_HOST__/mcp"
sys.path.insert(0, str(ROOT / "src"))


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def load(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"{path} must contain a JSON object")
    return value


def main() -> int:
    plugin = load(ROOT / "plugin.json")
    if plugin.get("$schema") != "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json":
        fail("plugin.json does not target Agent Plugins 1.0.0")
    for field in ("name", "version", "description"):
        if not isinstance(plugin.get(field), str) or not plugin[field].strip():
            fail(f"plugin.json is missing {field}")
    if plugin["name"] != "neyvro-gtm-intelligence":
        fail("unexpected plugin name")
    onboarding = plugin.get("extensions", {}).get("com.openai", {}).get("onboardingSkill")
    if onboarding != "./skills/gtm-automation-with-neyvro/SKILL.md":
        fail("onboarding skill path is missing or unsafe")
    if not (ROOT / onboarding[2:]).is_file():
        fail("onboarding skill does not exist")

    mcp = load(ROOT / "mcp.json")
    if mcp.get("$schema") != "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json":
        fail("mcp.json does not target Agent Plugins MCP 1.0.0")
    server = mcp.get("mcpServers", {}).get("neyvro")
    if not isinstance(server, dict) or server.get("type") != "streamable-http":
        fail("neyvro MCP server must use streamable-http")
    if not isinstance(server.get("url"), str) or not server["url"].endswith("/mcp"):
        fail("neyvro MCP URL must be an /mcp endpoint")
    auth = server.get("extensions", {}).get("com.openai", {}).get("auth", {})
    if auth.get("type") != "oauth" or auth.get("client", {}).get("mode") not in {"dcr", "cimd", "provided"}:
        fail("neyvro MCP server must declare OAuth authentication")

    skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
    if not skills:
        fail("no packaged skills found")
    inventory = load(ROOT / "assets/skill-inventory.json")
    expected = set(inventory["portable_core_skills"]) | set(inventory["neyvro_exclusive_intelligence_skills"]) | set(inventory["legacy_compatibility_skills"])
    actual = {path.parent.name for path in skills}
    if expected != actual:
        fail(f"skill inventory mismatch: missing={sorted(expected - actual)}, extra={sorted(actual - expected)}")
    for path in skills:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n") or "name:" not in text or "description:" not in text:
            fail(f"invalid Agent Skill metadata: {path.relative_to(ROOT)}")
    from neyvro.skill_library import validate
    errors = validate(ROOT / "skills")
    if errors:
        fail("skill library validation failed: " + "; ".join(errors))
    print(f"Portable plugin valid: {len(skills)} skills, OAuth MCP schema valid.")
    if server["url"] == PLACEHOLDER:
        print("Deployment status: BLOCKED (mcp.json requires the actual deployed Neyvro HTTPS endpoint).")
    else:
        print("Deployment status: configured endpoint present; verify it before release.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
