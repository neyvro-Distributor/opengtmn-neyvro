# Neyvro Agent Skills

Neyvro skills are portable Markdown contracts under `skills/<name>/SKILL.md`.
Agents should discover metadata first and load only the exact skill needed for
the current task. Public knowledge skills load without a Neyvro login.

## CLI

```bash
neyvro-skills validate
neyvro-skills list
neyvro-skills search evidence buyer
neyvro-skills load account-research
neyvro-skills build
```

The generated `index.json`, `llms.txt`, and `dist/neyvro-skills.md` are derived
artifacts. Do not edit them directly. A skill's `mode`, `required_scopes`,
`maturity`, and `related_skills` metadata are part of its compatibility contract.

Knowledge-only skills do not require the Neyvro MCP. Research, draft, and
external-action modes must follow the scopes and approval rules in the skill.
