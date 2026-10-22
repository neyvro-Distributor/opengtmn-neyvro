#!/usr/bin/env bash
set -euo pipefail

plugin_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
target="${1:-${CODEX_SKILLS_DIR:-}}"
if [[ -z "${target}" ]]; then
  echo "usage: $0 /path/to/codex/skills/neyvro" >&2
  echo "example: $0 ~/.codex/skills/neyvro" >&2
  exit 2
fi

mkdir -p "${target}"
find "${plugin_root}/skills" -mindepth 2 -maxdepth 2 -type f -name SKILL.md -print0 |
  while IFS= read -r -d '' skill_file; do
    skill_dir="$(dirname "${skill_file}")"
    skill_name="$(basename "${skill_dir}")"
    mkdir -p "${target}/${skill_name}"
    cp "${skill_file}" "${target}/${skill_name}/SKILL.md"
  done
echo "Installed $(find "${plugin_root}/skills" -mindepth 2 -maxdepth 2 -type f -name SKILL.md | wc -l | tr -d ' ') skills into ${target}"
