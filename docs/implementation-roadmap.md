# Portable Neyvro Agent Plugin implementation roadmap

This roadmap is file-level and ordered by dependency. It preserves the current
Neyvro API as the domain authority.

## Phase 0 — preserve the evidence base

1. Add `docs/opengtm-audit.md`, `docs/neyvro-gap-analysis.md`,
   `docs/skill-coverage.md`, and `docs/integration-contracts.md` (this audit).
2. Add a `reference/opengtm/NOTICE` containing the upstream MIT attribution if
   OpenGTM Markdown is copied instead of referenced.
3. Add `tools/audit_opengtm.py` to compare the pinned OpenGTM SHA, 17 skills,
   frontmatter, and generated artifacts without overwriting source skills.

Exit criteria: reproducible audit output and no license/branding ambiguity.

## Phase 1 — portable skill package

1. Create `plugin/skills/neyvro-*/SKILL.md` for the 17 mapped skills in
   `docs/skill-coverage.md`.
2. Create `plugin/manifest.json` with skill names, modes (`knowledge`,
   `read`, `proposal`, `execution`), required scopes, and API contract versions.
3. Create `plugin/tools/validate-skills.mjs`, reusing the reference validator's
   checks but adding required Neyvro metadata: `mode`, `backend_contract`,
   `required_scopes`, and `approval_required`.
4. Create `plugin/tools/build.mjs` to generate a manifest and single-file bundle.

Exit criteria: all plugin skills pass validation; execution skills cannot be
represented without a backend contract.

## Phase 2 — local MCP adapter

1. Create `plugin/mcp/server.mjs` with `initialize`, `tools/list`,
   `resources/list/read`, `prompts/list/get`, and the tools in the integration
   contract.
2. Create `plugin/mcp/neyvro-client.mjs` for API calls, session forwarding,
   timeout/error normalization, and request IDs.
3. Add `plugin/tests/mcp-smoke.mjs` for discovery, unknown skill, malformed
   JSON-RPC, and provider-blocked responses.

Exit criteria: local knowledge works without credentials; read tools fail closed
without an authenticated Neyvro session; no stdout logging contaminates JSON-RPC.

## Phase 3 — API gateway integration

1. Add `apps/api/app/plugin/` with schemas, capability discovery, and route
   adapters to onboarding, analysis, discovery, operations, mail, and
   investigation services.
2. Reuse `app.auth`, `app.workspaces`, `app.common.model_base`, and existing
   mailbox permission checks; do not build parallel tenant/auth models.
3. Add API tests for workspace isolation, role/scope enforcement, evidence
   provenance, draft approval, idempotent send, and reply-driven follow-up stop.

Exit criteria: every `IMPLEMENTED` mapping in the coverage document has a real
route/service and integration test.

## Phase 4 — client compatibility

1. Add Codex and Claude Code skill install/config recipes.
2. Add Cursor and generic MCP JSON examples.
3. Test ChatGPT only through the available connector surface and record the
   result; do not claim support from configuration examples alone.

Exit criteria: initialize, tools/list, resources/list, and one authorized read
workflow pass per supported client.

## Phase 5 — missing capability contracts

1. Define and implement an explicit digital-twin projection.
2. Define proposal-only SEO/GEO/content contracts before any publisher.
3. Define CRM/revenue attribution data sources and denominators.
4. Add LinkedIn only after an authorized provider contract exists.

Exit criteria: no capability is promoted from MISSING/BLOCKED without source,
credential, authorization, and tests.

## Current blockers

- No existing Neyvro MCP gateway or portable plugin package.
- No exact OpenGTM-equivalent 17 Neyvro skill files yet.
- No authorized LinkedIn, SEO/GEO publishing, or broad CRM provider contract.
- ChatGPT connector behavior is external and unverified.
