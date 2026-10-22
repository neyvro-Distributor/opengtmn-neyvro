# Contributing

Keep `skills/` as the single source of truth. Do not add client-specific skill
forks. Changes to skills must preserve valid YAML frontmatter, activation
conditions, authorization boundaries, and evidence/uncertainty handling.

Before opening a pull request:

```bash
python3 scripts/validate_release.py
python3 scripts/validate_plugin.py
python3 -m neyvro.skill_cli build
pytest -q
git diff --check
```

Do not include credentials, customer records, bearer tokens, or real outreach
recipients in fixtures. External sends, publishing, and deployment changes
require explicit review and are not performed by tests.
