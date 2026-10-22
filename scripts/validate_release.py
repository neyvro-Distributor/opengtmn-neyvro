"""Mandatory release gate for skills and generated plugin artifacts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main() -> int:
    from neyvro.skill_library import discover, validate

    mandatory = json.loads((ROOT / "assets/mandatory-skills.json").read_text())
    required = set(mandatory["required_open_gtm_equivalent"]) | set(mandatory["required_neyvro_exclusive"])
    skills = discover(ROOT / "skills")
    actual = {skill.name for skill in skills}
    errors = validate(ROOT / "skills")
    missing = sorted(required - actual)
    if missing:
        errors.append("missing mandatory skills: " + ", ".join(missing))
    for skill in skills:
        if skill.name not in required:
            continue
        body = skill.markdown.split("---", 2)[-1].strip()
        if len(body) < 600:
            errors.append(f"{skill.name}: substantive instructions are too short")
        if re.search(r"\b(?:TODO|TBD|placeholder skill)\b", body, re.IGNORECASE):
            errors.append(f"{skill.name}: TODO/TBD placeholder content is not allowed")
        structural_signals = (
            "activation", "workflow", "mcp", "approval", "evidence",
            "uncertainty", "authorization", "output", "input", "test",
        )
        signal_count = sum(term in body.casefold() for term in structural_signals)
        if signal_count < 2:
            errors.append(f"{skill.name}: missing substantive workflow signals")
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print(f"PASS mandatory skill gate: {len(required)} required skills; {len(skills)} packaged skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
