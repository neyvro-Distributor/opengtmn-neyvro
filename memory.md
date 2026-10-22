# Project Memory

This file records the work implemented in this repository so the project history remains easy to review and continue.

## Current project status

- Repository: `opengtmn-neyvro-`
- Branch: `main`
- Current baseline: initial repository setup
- License: GNU General Public License v3.0, stored in [`LICENSE`](./LICENSE)
- Application/source code: not added yet

## Work log

### 2026-10-22

- Created the repository baseline with the GNU GPL v3.0 license.
- Added this `memory.md` file to track implemented work and future project decisions.

### 2026-10-22 — Initial Neyvro foundation

- Implemented a dependency-light tenant-scoped domain foundation for companies, evidence, and approval requests.
- Implemented scope checks for intelligence reads, proposal writes, and outbound-message approval.
- Added a 26-entry skill contract catalog and validation function.
- Added unit tests covering catalog size, tenant isolation, scope enforcement, evidence, and approval gating.
- Added [`docs/IMPLEMENTATION_STATUS.md`](./docs/IMPLEMENTATION_STATUS.md) and [`docs/NEXT_STEPS.md`](./docs/NEXT_STEPS.md).
- External MCP, OAuth, provider, mailbox, plugin, and deployment integrations remain explicitly blocked or not started because this repository contains no service contracts or credentials for them.

### 2026-10-22 — OpenGTM and Neyvro platform audit

- Audited OpenGTM at commit `fedfaebbfbc435c671ec6298dbe0a40a07f9b5d0`.
- Verified all 17 reference skills, the local knowledge-only MCP server, build artifacts, plugin manifests, MIT license, and validation behavior.
- Inspected the Neyvro API repository at commit `4dee606`; its existing API test suite passed with `1046 passed in 130.77s`.
- Classified onboarding, discovery, monitoring/evidence, predictions, buyer intelligence, mailbox integrations, follow-ups, and workspace operations using actual source files.
- Added the OpenGTM audit, Neyvro gap analysis, skill coverage map, integration contracts, and file-level implementation roadmap under `docs/`.

### 2026-10-22 — Portable skill library infrastructure

- Added the canonical `skills/` directory with 26 contract-phase skills: the 17 OpenGTM-compatible GTM identifiers and 9 Neyvro intelligence identifiers.
- Added YAML frontmatter validation, exact skill loading, metadata/content search, related-skill checks, credential scanning, version tracking, and deterministic artifact generation in `src/neyvro/skill_library.py`.
- Added the `neyvro-skills` CLI, `AGENTS.md` entrypoint, generated `index.json`, `llms.txt`, and `dist/neyvro-skills.md`.
- Added valid/invalid fixtures, unit tests, and `.github/workflows/skills.yml` CI checks.
- Kept all skills explicitly at `maturity: contract`; substantive playbooks remain for later implementation prompts.

### 2026-10-22 — GTM strategy skill

- Upgraded `skills/gtm-strategy/SKILL.md` from a contract stub to a substantive Neyvro playbook covering product context, economics, industries/regions, buyers, motion comparison, channels, crawl/walk/run planning, outputs, evidence, and research gaps.
- Added disabled-by-default contracts for `neyvro_get_customer_context`, `neyvro_get_gtm_strategy`, and `neyvro_propose_gtm_strategy` in `skills/gtm-strategy/integration.json`.
- Added a knowledge-safe recommendation engine in `src/neyvro/gtm_strategy.py`; it works without login and only uses a real backend when an adapter is explicitly injected.
- Added realistic SMB SaaS, enterprise security, developer-tool, missing-context, and contract tests.

## Future entries

When implementing new work, add an entry using this format:

```markdown
### YYYY-MM-DD — Short title

- Implemented: what was added or changed.
- Files: files created or modified.
- Verification: tests, checks, or manual validation performed.
- Notes: important decisions, limitations, or follow-up work.
```

## Outstanding work

- Define the project purpose and initial requirements.
- Add the first application/source implementation.
- Add setup instructions and verification steps once implementation begins.
