# Neyvro skills infrastructure

The canonical skill library lives in `skills/`. Each skill is a portable
`SKILL.md` with required `name` and activation-oriented `description` fields.
The current 35 files are contract-phase definitions: they define behavior
boundaries and backend expectations while later work adds substantive playbooks.

## Discovery and context control

Use `neyvro-skills list` or `index.json` to discover metadata, then
`neyvro-skills load <exact-name>` for one skill. `search` ranks metadata and
content matches. Agents must not inject the consolidated bundle into every
request; `dist/neyvro-skills.md` exists for explicit bulk-import use only.

## Generated artifacts

`neyvro-skills build` deterministically generates:

- `index.json` — versioned metadata registry.
- `llms.txt` — lightweight discovery entrypoint.
- `dist/neyvro-skills.md` — consolidated Markdown bundle.

These files are derived from `skills/*/SKILL.md` and must not be edited directly.

## Validation

`neyvro-skills validate` checks frontmatter, kebab-case identifiers, directory
matching, semantic versions, duplicate names, related-skill references, local
Markdown links, credential-like content, and required files. CI also runs the
unit tests and rebuilds artifacts twice to verify deterministic output.

## Maturity and modes

Every skill records `maturity`, `mode`, `required_scopes`, and
`related_skills`. `contract` is intentionally distinct from a completed
`playbook` or `verified` skill. Knowledge-only skills load without a Neyvro
login; research and external-action behavior is blocked until the documented
Neyvro service contracts and approval flows exist.
