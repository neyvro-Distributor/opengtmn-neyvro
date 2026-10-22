# Neyvro Implementation Status

This checklist reflects only work actually present and verified in the repository.

| Requirement | Status | Files | Tests | Blocker |
|---|---|---|---|---|
| Repository baseline and licensing | VERIFIED | `LICENSE` | Git inspection | None |
| Persistent implementation tracking | IMPLEMENTED | `memory.md`, `docs/NEXT_STEPS.md` | Markdown inspection | None |
| Tenant-scoped domain foundation | IMPLEMENTED | `src/neyvro/models.py`, `src/neyvro/service.py` | `tests/test_foundation.py` | None |
| Scope-based authorization | IMPLEMENTED | `src/neyvro/models.py`, `src/neyvro/service.py` | Tenant/scope tests | None |
| Evidence-backed company records | IMPLEMENTED | `src/neyvro/models.py`, `src/neyvro/service.py` | Evidence flow test | None |
| Approval-gated outbound action proposal | IMPLEMENTED | `src/neyvro/models.py`, `src/neyvro/service.py` | Approval flow test | Real mailbox connector not available |
| 26-skill contract catalog | IMPLEMENTED | `src/neyvro/skills.py` | Catalog validation test | Exact 17 OpenGTM names not supplied |
| OpenGTM reference audit | VERIFIED | `docs/opengtm-audit.md` | OpenGTM validator/build/MCP smoke checks | None |
| Neyvro capability gap analysis | VERIFIED | `docs/neyvro-gap-analysis.md`, `docs/skill-coverage.md` | Neyvro API suite: 1046 passed | External plugin contracts remain |
| Portable plugin integration contracts | IMPLEMENTED | `docs/integration-contracts.md`, `docs/implementation-roadmap.md` | Contract review only | Gateway and client adapters not implemented |
| Canonical 26-skill library | IMPLEMENTED | `skills/*/SKILL.md`, `src/neyvro/skill_library.py` | `tests/test_skill_library.py` | Playbook content remains contract-phase |
| Skill registry, loader, search, and validator CLI | VERIFIED | `src/neyvro/skill_library.py`, `src/neyvro/skill_cli.py` | 10 skill tests passed | None |
| Deterministic manifests and bundle | VERIFIED | `index.json`, `llms.txt`, `dist/neyvro-skills.md` | Determinism test and CLI build | None |
| Skill CI checks and fixtures | IMPLEMENTED | `.github/workflows/skills.yml`, `tests/fixtures/**` | Local pytest and validation | Remote GitHub runner not executed here |
| `gtm-strategy` substantive playbook | VERIFIED | `skills/gtm-strategy/SKILL.md`, `skills/gtm-strategy/integration.json`, `src/neyvro/gtm_strategy.py` | `tests/test_gtm_strategy.py` | Connected API adapter unavailable; safely disabled |
| Local knowledge MCP server | NOT STARTED | — | — | MCP SDK/protocol contract not supplied |
| Remote Streamable HTTP MCP server | BLOCKED | — | — | Hosting, domain and auth provider required |
| OAuth and customer identity integration | BLOCKED | — | — | Identity provider and client credentials required |
| Company research and contact integrations | BLOCKED | — | — | Authorized provider credentials and API contracts required |
| Cross-tenant production authorization tests | IMPLEMENTED | `src/neyvro/service.py` | Tenant isolation test | Production identity integration pending |
| Duplicate-send and reply-stop workflows | NOT STARTED | — | — | Mailbox provider and event contract required |
| Plugin manifests for Codex/Claude/Cursor/ChatGPT | NOT STARTED | — | — | Client-specific manifest contracts required |
| Docker and CI deployment | NOT STARTED | — | — | Runtime/deployment target not supplied |
