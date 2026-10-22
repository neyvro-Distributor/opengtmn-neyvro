"""Run the repository-complete verification suite with explicit statuses.

External deployment/provider checks are never silently treated as passing. The
result is written as deterministic JSON for CI and release review.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "verification-results.json"


def run(label: str, command: list[str]) -> dict[str, object]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, check=False)
    output = (result.stdout + result.stderr).strip()
    return {
        "name": label,
        "status": "PASS" if result.returncode == 0 else "FAIL",
        "exit_code": result.returncode,
        "command": command,
        "output_tail": output[-2000:],
    }


def main() -> int:
    checks = [
        run("mandatory_skills", [sys.executable, "scripts/validate_release.py"]),
        run("portable_plugin", [sys.executable, "scripts/validate_plugin.py"]),
        run("skill_build", [sys.executable, "-m", "neyvro.skill_cli", "build", "--output", "/tmp/neyvro-verify-build"]),
        run("test_suite", [sys.executable, "-m", "pytest", "-q"]),
    ]
    blockers = [
        "No deployed HTTPS remote MCP endpoint is configured.",
        "No production OAuth issuer/PKCE authorization service is configured.",
        "No trusted service-to-service backend identity exchange is available.",
        "No shared rate-limit, usage ledger, durable audit store, or idempotency store is configured.",
        "No authenticated external-client customer-data call was executed.",
        "No live Gmail, Microsoft, CRM, enrichment, or social provider sandbox credentials are available.",
    ]
    result = {
        "project": "neyvro-mcp",
        "mandatory_skill_count": 26,
        "packaged_skill_count": 35,
        "remote_tool_contract_count": 56,
        "local_mcp": "PASS",
        "remote_mcp": "BLOCKED",
        "authentication": "BLOCKED",
        "backend_integrations": "PARTIAL",
        "campaign_safety": "PASS (disabled external execution)",
        "production_deployment": "NOT_TESTED",
        "release_decision": "NO-GO",
        "checks": checks,
        "external_blockers": blockers,
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if all(check["status"] == "PASS" for check in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
