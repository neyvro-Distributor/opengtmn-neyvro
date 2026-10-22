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

### 2026-10-23 — ICP skill

- Upgraded `skills/ideal-customer-profile/SKILL.md` to a complete ICP playbook covering firmographics, technographics, size/geography, personas, problems, triggers, anti-ICP rules, weighted scoring, A/B/C tiers, and evidence-backed refinement.
- Added `src/neyvro/icp.py` with deterministic fit evaluation, multiple-signal qualification requirements, nonmatching/incomplete/disqualified states, and fail-closed adapter contracts.
- Added disabled-by-default contracts for `neyvro_get_icp`, `neyvro_evaluate_icp_fit`, and `neyvro_propose_icp_changes`.
- Added realistic matching, nonmatching, incomplete, disqualified, and backend-disabled tests.

### 2026-10-23 — Positioning and messaging skill

- Upgraded `skills/positioning-and-messaging/SKILL.md` to a complete product-positioning workflow covering category, alternatives, capabilities, customer problems, before/after/bridge, value propositions, battlecards, personas, approved voice, objections, message houses, versioning, and approval status.
- Added `src/neyvro/positioning.py` with evidence-safe draft generation, approved-claim filtering, unsupported-claim reporting, persona-specific angles, and fail-closed adapter contracts.
- Added disabled-by-default contracts for `neyvro_get_product_context`, `neyvro_get_positioning`, `neyvro_propose_positioning`, and `neyvro_get_approved_claims`.
- Added security-persona, developer-persona, incomplete-context, and disabled-backend tests.

### 2026-10-23 — Account research skill

- Upgraded `skills/account-research/SKILL.md` to a company-digital-twin workflow covering business model, firmographics, technology, changes, hiring, leadership, expansion, funding, product, buyers, relationship authorization, freshness, account-tier budgets, evidence classes, disqualifiers, and one safe outreach angle.
- Added `src/neyvro/account_research.py` with bounded deterministic briefs, stale/contradictory/not-found/unauthorized handling, cited evidence, negative evidence, tier budgets, and injected MCP adapter contracts.
- Added disabled-by-default contracts for `neyvro_research_company`, `neyvro_get_company_twin`, `neyvro_get_company_signals`, `neyvro_get_company_timeline`, and `neyvro_get_evidence`.
- Added tests for supported and negative evidence, contradictory signals, stale research, nonexistent and unauthorized companies, budget reporting, and adapter behavior.

### 2026-10-23 — Lead sourcing and enrichment skill

- Upgraded `skills/lead-sourcing-and-enrichment/SKILL.md` to a complete ICP-filtered buyer discovery workflow covering role inference, buying committees, CRM/opportunity matching, provider waterfalls, verification, freshness, deduplication, suppression, existing-customer exclusions, permitted use, cost, entitlement, and rate limits.
- Added `src/neyvro/lead_sourcing.py` with structured contact responses, provenance, guessed-email protection, catch-all/stale states, wrong-company filtering, provider failure events, paid-provider budget gates, and injected MCP adapter contracts.
- Added disabled-by-default contracts for `neyvro_search_buyers`, `neyvro_get_opportunity_buyers`, `neyvro_enrich_contact`, and `neyvro_get_contact_verification`.
- Added tests for verified and unverified contacts, catch-all domains, duplicates, wrong-company matches, opt-outs, stale verification, provider failures, missing entitlement, sample structured output, and adapter behavior.

### 2026-10-23 — Cold email writing skill

- Upgraded `skills/cold-email-writing/SKILL.md` to an evidence-grounded, draft-only outbound workflow supporting PAS, BAB, AIDA, trigger-first personalization, buyer-role framing, one-ask CTAs, follow-up variants, and explicit claim/approval rules.
- Added `src/neyvro/cold_email.py` with structured drafts, prospect-claim validation, stale/unverified/missing evidence flags, suppression and existing-customer blocks, and a permanently false `send_allowed` field.
- Added disabled-by-default contracts for `neyvro_draft_email`, `neyvro_check_message_claims`, and `neyvro_get_email_draft`; follow-up integration is limited to supported draft/review adapters.
- Added tests for unsupported claims, poor/stale personalization, missing evidence, multiple buyer roles, suppressed recipients, claim checking, sample output, and adapter behavior.

### 2026-10-23 — Email deliverability skill

- Upgraded `skills/email-deliverability/SKILL.md` to a read-only sender-safety workflow covering Gmail/Microsoft connection status, SPF, DKIM, DMARC, sender identity, limits, ramp guidance, verification, bounces, complaints, unsubscribes, suppression, and unknown metrics.
- Added `src/neyvro/deliverability.py` with structured configuration audits, provider health signals, hard safety blocks, explicit DNS authorization handling, no inbox-placement invention, and injected read-only MCP adapters.
- Added disabled-by-default contracts for `neyvro_get_mailbox_health`, `neyvro_get_sender_limits`, `neyvro_get_delivery_metrics`, and `neyvro_audit_email_configuration`.
- Added tests for missing DNS records, disconnected mailboxes, exceeded limits, repeated bounces, unverified/suppressed recipients, unauthorized DNS inspection, adapter setup, and the permanent no-send boundary.

### 2026-10-23 — LinkedIn outreach skill

- Upgraded `skills/linkedin-outreach/SKILL.md` to an authorized, assisted LinkedIn workflow covering professional buyer context, current-role freshness, evidence-backed angles, connection notes, direct-message gating, meaningful engagement suggestions, relationship-aware follow-up, and manual confirmation.
- Added `src/neyvro/linkedin.py` with tenant-safe context reads, stale/missing profile handling, unsupported automation states, connected-relationship checks, opt-out blocking, manual action recording, and injected MCP adapters.
- Added disabled-by-default contracts for `neyvro_get_linkedin_prospect_context`, `neyvro_draft_linkedin_message`, `neyvro_get_social_relationship`, and `neyvro_record_manual_outreach`.
- Added tests for missing profiles, stale roles, unsupported actions, cross-tenant records, opt-outs, relationship gating, manual confirmation, evidence use, and disabled-provider behavior.

### 2026-10-23 — Multichannel sequences skill

- Upgraded `skills/multichannel-sequences/SKILL.md` to a declarative campaign-planning and orchestration workflow covering email, LinkedIn-assisted and authorized social steps, scheduling, branches, preconditions, stop rules, approval versions, sender/recipient eligibility, and the full campaign lifecycle.
- Added `src/neyvro/sequences.py` with deterministic state-machine compilation, stable job IDs, eligibility rechecks, idempotent duplicate-job handling, concurrent reply stops, approval revocation checks, paused-campaign protection, injected scheduler support, and no arbitrary code execution.
- Added disabled-by-default contracts for `neyvro_propose_campaign`, `neyvro_create_campaign_draft`, `neyvro_get_campaign`, `neyvro_pause_campaign`, and `neyvro_get_campaign_status`.
- Added tests for deterministic compilation, full approval/scheduling/dispatch flow, duplicate jobs, concurrent replies, revoked approval, unsupported channels/conditions, paused campaigns, scheduler injection, and disabled adapters.

### 2026-10-23 — Outreach personalization skill

- Upgraded `skills/outreach-personalization/SKILL.md` to an evidence-linked personalization-at-scale workflow with high-touch strategic, medium-touch qualified, and lightweight relevant effort levels.
- Added reusable verified-trigger, why-now, pain-hypothesis, product-benefit, proof-point, and CTA snippets with generic-message labeling, buyer-role matching, confidence limitations, brand-voice versioning, contradiction detection, and permanent no-send behavior.
- Added disabled-by-default contracts for `neyvro_get_personalization_context`, `neyvro_generate_personalization`, `neyvro_validate_outreach_claims`, and `neyvro_get_brand_voice`.
- Added tests for evidence mismatch, buyer-role mismatch, low-information accounts, contradictory signals, brand-voice consistency/hype, structured snippets, and disabled adapters.

### 2026-10-23 — Reply handling and objections skill

- Upgraded `skills/reply-handling-and-objections/SKILL.md` to a thread-aware reply workflow covering all requested reply categories, conversation retrieval, classification evidence, objection/meeting drafts, human review, opt-out enforcement, and stop-on-reply behavior.
- Added `src/neyvro/replies.py` with deterministic baseline classification, tenant/thread validation, duplicate webhook idempotency, safety-critical unsubscribe/rejection suppression, follow-up stop state, and no-send drafting.
- Added disabled-by-default contracts for `neyvro_get_conversation`, `neyvro_get_reply_status`, `neyvro_classify_reply`, `neyvro_draft_reply`, and `neyvro_get_followup_queue`, with separate read/draft/send permission boundaries.
- Added tests for interested/meeting replies, hard rejection, unsubscribe, wrong person, out-of-office, objections, duplicate webhooks, wrong threads, unknown replies, tenant isolation, and disabled adapters.

### 2026-10-23 — Discovery and qualification skill

- Upgraded `skills/discovery-and-qualification/SKILL.md` to an evidence-backed BANT, MEDDIC, and MEDDPICC workflow covering account briefings, qualification dimensions, buying committees, pain severity, objections, disqualification, discovery questions, and read-only next steps.
- Added `src/neyvro/qualification.py` with explicit verified-fact requirements, unknown budget/timing protection, conflict detection, nonbuyer/disqualified states, committee mapping, CRM/meeting research gaps, and injected MCP adapters.
- Added disabled-by-default contracts for `neyvro_get_opportunity_qualification`, `neyvro_generate_discovery_brief`, `neyvro_get_buying_committee`, and `neyvro_get_meeting_context`.
- Added tests for incomplete, explicitly qualified, conflicting, nonbuyer, disqualified, MEDDPICC committee, missing CRM/meeting context, and disabled-adapter behavior.

### 2026-10-23 — SEO fundamentals skill

- Upgraded `skills/seo-fundamentals/SKILL.md` to an optional, authorized, robots-aware SEO audit workflow covering crawlability, indexing, redirects, metadata, headings, internal links, content relevance, mobile/page experience, structured data, severity, priority, and verification checklists.
- Added `src/neyvro/seo.py` with bounded snapshot analysis, invalid/inaccessible/partial crawl handling, explicit unknown performance metrics, actionable issue recommendations, and review-only repository change proposals.
- Added disabled-by-default contracts for `neyvro_analyze_website`, `neyvro_get_seo_recommendations`, and `neyvro_propose_seo_changes`; merge/deploy is permanently unsupported.
- Added tests for invalid/inaccessible sites, robots gating, redirects, missing metadata, partial/rate-limited crawls, unknown metrics, unauthorized repository access, reviewable proposals, and disabled adapters.

### 2026-10-23 — Generative engine optimization skill

- Upgraded `skills/generative-engine-optimization/SKILL.md` to an evidence-labeled GEO/AEO workflow covering crawler access, answer-first content, citations, schema, entity consistency, authority, freshness, optional `llms.txt`, and measurement planning.
- Added `src/neyvro/geo.py` with bounded authorized-snapshot audits, explicit conflicts and unknowns, unavailable visibility handling, and review-only repository proposals.
- Added disabled-by-default contracts for `neyvro_get_geo_audit`, `neyvro_get_ai_visibility_findings`, and `neyvro_propose_geo_improvements`; no website changes, merges, deploys, or fabricated engine measurements.
- Added tests for malformed schema, crawler restrictions, missing/conflicting data, unsupported visibility measurements, repository authorization, and disabled adapters.

### 2026-10-23 — Content marketing engine skill

- Upgraded `skills/content-marketing-engine/SKILL.md` to an evidence-grounded content workflow covering buyer-question ideation, editorial briefs, drafting, repurposing, channel norms, measurement limits, lifecycle states, and explicit approval.
- Added `src/neyvro/content_marketing.py` with deterministic ideas, claim-reviewed drafts, channel checks, duplicate publication detection, approval-gated social proposals, and disabled-by-default adapters.
- Added contracts for `neyvro_generate_content_ideas`, `neyvro_create_content_brief`, `neyvro_draft_content`, `neyvro_get_content_calendar`, and `neyvro_propose_social_post`.
- Added tests for draft quality, incomplete claims, brand voice, unsupported channels, authorization/approval gating, duplicate publication, and disabled adapters.

### 2026-10-23 — Outbound metrics and benchmarks skill

- Upgraded `skills/outbound-metrics-and-benchmarks/SKILL.md` to an explicit-denominator outbound analytics workflow covering contacts, verification, delivery, bounce, replies, meetings, opportunities, pipeline, outcomes, revenue attribution, costs, segmentation, sample sizes, and causal limits.
- Added `src/neyvro/outbound_metrics.py` with tenant/window/segment filtering, duplicate event handling, inconsistent-event warnings, zero-denominator protection, contextual benchmark comparison, and evidence-tied recommendations.
- Added disabled-by-default contracts for `neyvro_get_campaign_metrics`, `neyvro_get_pipeline_metrics`, `neyvro_get_revenue_attribution`, and `neyvro_get_signal_performance`.
- Added tests for funnel aggregation, zero denominators, missing CRM outcomes, duplicate/inconsistent events, tenant isolation, contextual benchmarks, sample-size recommendations, and disabled adapters.

### 2026-10-23 — GTM automation with Neyvro skill

- Added `skills/gtm-automation-with-neyvro/SKILL.md` as the Neyvro-native bridge from portable knowledge skills to capability discovery and approved execution; it does not require Chronos accounts, APIs, or `geo_*` tools.
- Added `src/neyvro/gtm_automation.py` with a complete skill-to-Neyvro-tool map, connection/authentication/scope/service/account discovery, server-equivalent action gates, approval checks, workflow phases, and disconnected knowledge-only behavior.
- Added discovery contracts for `neyvro_get_capabilities`, `neyvro_get_connections`, `neyvro_get_permissions`, and `neyvro_get_approval_status`, plus `integration.json`.
- Expanded the canonical registry from 26 to 27 skills and added tests for disconnected, invalid-auth, insufficient-scope, unavailable-service, pending-approval, approved-gate, secret-redaction, native-tool mapping, and disabled-adapter states.

### 2026-10-23 — Company intelligence and predictive GTM skills

- Added nine specialized skills: `company-digital-twin-analysis`, `technology-change-detection`, `predictive-problem-intelligence`, `evidence-verification`, `buying-window-detection`, `buyer-opportunity-matching`, `continuous-account-investigation`, `negative-evidence-analysis`, and `revenue-attribution`.
- Added valid skill metadata, activation conditions, inputs/outputs, evidence and uncertainty rules, authorization boundaries, MCP contracts, and per-skill integration manifests.
- Added `src/neyvro/intelligence_skills.py` with tenant-scoped read-only twin analysis, stale/conflicting evidence handling, hypothesis-only prediction, buying-window checks, buyer matching, budgeted investigation planning, negative evidence, attribution limits, and fail-closed adapters.
- Expanded the canonical registry from 27 to 35 skills and extended the Neyvro GTM automation map. Revenue attribution was upgraded in place; the eight missing specialized skill directories were added. Added tests for supported, conflicting, missing, stale, unauthorized, budget-limited, cross-tenant, and incomplete revenue evidence.

### 2026-10-23 — Local Neyvro Skills MCP server

- Added `src/neyvro/mcp_server.py` using the official Python MCP SDK `FastMCP` stdio transport; no handwritten JSON-RPC parser and no customer-data execution service.
- Exposed `neyvro_list_skills`, `neyvro_get_skill`, and `neyvro_search_skills`, plus bounded `neyvro://skills/<skill-name>` resources and one prompt per canonical skill.
- Added installable `neyvro-mcp-skills` entry point, `README.md`, `docs/mcp-local-server.md`, and `examples/mcp/neyvro-local-skills.json` with startup and client configuration instructions.
- Added a real local `ClientSession` protocol test for tools/list, tools/call, resources/list, resources/read, prompts/list, prompts/get, exact content, argument validation, unknown skills, and 35 registrations. Public skills work without Neyvro login and no filesystem paths or private records are exposed.

### 2026-10-23 — Remote Streamable HTTP MCP boundary

- Added `src/neyvro/remote_mcp.py` with the official MCP SDK Streamable HTTP transport, 56 requested tool contracts, Pydantic schemas, explicit READ/RESEARCH/DRAFT/PROPOSE/APPROVE/EXECUTE/PUBLISH modes, scope gates, tenant checks, bounded pagination, approval checks, safe errors, backend adapter isolation, and fail-closed readiness states.
- Added `neyvro-mcp-remote` packaging entrypoint and `docs/remote-mcp-readiness.md` documenting startup, OAuth/JWT requirements, provider-assigned HTTPS hosting, tool statuses, backend blockers, and security work required before public customer-data exposure.
- Added `tests/test_remote_mcp.py` covering catalog uniqueness, anonymous access, tenant mismatch, missing scopes, pending approval, SSRF literal-address rejection, inbound-token non-forwarding, and transport registration.
- Verification: 8 focused remote MCP tests passed; an elevated Uvicorn smoke test completed the MCP initialize handshake and `tools/list` over `http://127.0.0.1:8765/mcp` (56 tools). The live backend adapter remains disabled because the existing backend uses Firebase-to-session-cookie auth and lacks the trusted OAuth tenant exchange.

### 2026-10-23 — Portable Neyvro Agent Plugin package

- Added the current Agent Plugins 1.0.0 package layout: root `plugin.json`, OAuth-configured `mcp.json`, `.codex-plugin/plugin.json` compatibility overlay, `assets/skill-inventory.json`, and asset documentation.
- Packaged all 35 current skill directories: 17 OpenGTM-equivalent workflows, 9 Neyvro-exclusive intelligence skills, and 9 legacy compatibility documents. The Neyvro-native automation skill is the supported bridge; the Chronos-named document is retained only for compatibility.
- Added `scripts/install-codex-skills.sh` for explicit installation into a supported local Codex skills directory and `scripts/validate_plugin.py` for manifest, OAuth, path, inventory, YAML/frontmatter, related-reference, and credential checks.
- Added [docs/agent-plugin.md](docs/agent-plugin.md) and updated `README.md` with current Codex CLI MCP commands, OAuth setup, ChatGPT custom MCP/plugin testing, local skill installation, sample requests, and public submission limitations.
- Verification: plugin validator passed with 35 skills and correctly reports deployment `BLOCKED` because no deployed Neyvro HTTPS endpoint exists in the workspace; Codex CLI discovery and 35-skill installation smoke test passed; plugin tests passed (3), full suite remains passing (132 expected after test collection).

### 2026-10-23 — Claude Code plugin integration

- Added `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` using the current Claude Code plugin and marketplace layouts. The plugin reuses the exact canonical root `skills/` directory; it does not create a second skill tree.
- Added `README-CLAUDE.md` with Git marketplace installation, update/uninstall, local checkout validation, remote OAuth MCP setup, local stdio MCP setup, offline behavior, safe approval boundaries, and sample Neyvro requests.
- Added Claude MCP examples at `examples/claude/neyvro-local.mcp.json` and `examples/claude/neyvro-remote.mcp.json`; the remote example uses `${NEYVRO_MCP_URL}` and contains no credentials.
- Verification: installed Claude Code `2.1.273`; `claude plugin validate .claude-plugin/plugin.json` and `claude plugin validate .` passed; Claude-specific package tests passed (4); skill/plugin validation and `git diff --check` passed. Remote OAuth and read-only customer-data calls remain blocked until a real deployed Neyvro endpoint and identity provider are available. `claude mcp list` was not treated as a package failure because this installation health-checks unrelated configured MCP servers and exceeded the command timeout.

### 2026-10-23 — Cross-agent plugin and MCP compatibility

- Implemented: Cursor installation guidance, a Cursor MCP example, and documented compatibility paths for Windsurf/Devin Cascade, Cline, Continue, Zed, VS Code GitHub Copilot Agent mode, Gemini CLI, and generic MCP clients.
- Files: `.cursor/mcp.json.example`, `docs/cursor-installation.md`, `docs/client-compatibility.md`, `docs/other-agents.md`, `examples/client-configurations/`, and `tests/test_client_compatibility.py`.
- Verification: all client JSON/YAML fixtures parse; compatibility tests passed (5); full pytest suite passed (138); `scripts/validate_plugin.py` passed with 35 skills and correctly reported the missing deployed HTTPS endpoint.
- Notes: the root `plugin.json`, `mcp.json`, and `skills/` remain canonical. Cursor and other newly documented clients are `DOCUMENTED_ONLY`; no OAuth credentials or fictional production URL were added. Remote customer-data execution remains blocked until deployment and identity-provider setup.

### 2026-10-23 — Release engineering and public-readiness audit

- Implemented: mandatory 26-skill release inventory/gate, substantive-content checks, MCP Registry metadata draft, changelog, security policy, contribution policy, and release/security/MCP/skill/publication reports.
- Files: `assets/mandatory-skills.json`, `scripts/validate_release.py`, `.mcp/server.json`, `CHANGELOG.md`, `SECURITY.md`, `CONTRIBUTING.md`, and `docs/{skill-coverage-report,mcp-test-report,security-audit,publication-status,release-readiness}.md`.
- Verification: mandatory gate passed (26 required, 35 packaged); portable plugin validation passed; official MCP Registry `2025-12-11` schema validation passed; `PYTHONPATH=src python3 -m neyvro.skill_cli build` passed; full pytest passed (141); `git diff --check` passed.
- Notes: final public release is NO-GO. No deployed HTTPS remote endpoint, OAuth issuer, trusted backend identity exchange, shared rate/usage/audit controls, complete two-tenant workflow, or authenticated external-client read call is available. Local knowledge MCP is the only verified runnable distribution surface.

### 2026-10-23 — Deep MCP audit and verification gate

- Implemented: six missing remote MCP contract tools (`neyvro_get_monitoring_status`, `neyvro_get_opportunity_history`, `neyvro_get_buying_window`, `neyvro_evaluate_icp_fit`, `neyvro_get_contact_verification`, and `neyvro_list_campaigns`), public skill resources/prompts on the remote server, and the `make verify-all` completeness command.
- Files: `src/neyvro/remote_mcp.py`, `tests/test_remote_mcp.py`, `scripts/verify_all.py`, `Makefile`, `docs/COMPLETE_GAP_AUDIT.md`, `docs/ARCHITECTURE_VERIFICATION.md`, `docs/BACKEND_INTEGRATION_MAP.md`, `docs/TEST_EVIDENCE.md`, `docs/VERIFICATION_RESULTS.md`, and `docs/EXTERNAL_BLOCKERS.md`.
- Verification: 56 remote tool contracts, 35 remote public skill resources/prompts, mandatory 26-skill gate passed, and full suite passed (141 tests).
- Notes: remote customer-data functionality remains BLOCKED/PARTIAL without deployment, OAuth/PKCE, trusted backend identity exchange, shared controls, and provider sandboxes. Final release decision remains NO-GO.

### 2026-10-23 — Real E2E connection audit

- Implemented: `make test-e2e`, local HTTP health verification, and the complete `docs/e2e/` evidence set covering initial audit, protocol, skills, remote endpoint, OAuth, Codex, ChatGPT, cross-client comparison, security, blockers, and next steps.
- Verification: local remote app started on loopback and returned a real `/health` response; Codex CLI `0.163.0` was inspected and has no Neyvro entry; `make test-e2e` passed all repository checks with 141 tests.
- Notes: no real Codex private-tool call or ChatGPT custom-MCP conversation was claimed. Both remain BLOCKED/NOT_TESTED because no deployed HTTPS endpoint, OAuth provider, or backend credentials exist. MCP Inspector package resolution also remained NOT_TESTED.

### 2026-10-23 — Production unblocking audit

- Implemented: validated the Render Docker Blueprint, added the production deployment container/configuration, and completed the independent backend and repository verification gates.
- Files: `Dockerfile`, `.dockerignore`, `render.yaml`, `pyproject.toml`, `docs/e2e/REMOTE_ENDPOINT_RESULTS.md`, and `docs/e2e/BLOCKERS.md`.
- Verification: backend targeted suite passed 225 tests; Neyvro MCP suite passed 141 tests; `make verify-all` passed all local checks; plugin and release validators passed; Render Blueprint validation passed.
- Notes: production remains NO-GO. Render has no deployed Neyvro service, no public HTTPS MCP endpoint, no production OAuth/PKCE issuer, and no trusted backend service-identity exchange. Docker image build was not completed because the Docker daemon was unavailable. No broad push or deployment was performed.

### 2026-10-23 — Production blocker report

- Implemented: added the required production unblock, OAuth, backend-auth-bridge, Render, Codex, ChatGPT, and release-readiness reports.
- Files: `docs/PRODUCTION_UNBLOCK_REPORT.md`, `docs/OAUTH_INTEGRATION_RESULTS.md`, `docs/BACKEND_AUTH_BRIDGE.md`, `docs/RENDER_DEPLOYMENT_RESULTS.md`, `docs/CODEX_LIVE_TEST.md`, `docs/CHATGPT_LIVE_TEST.md`, and `docs/RELEASE_READINESS.md`.
- Verification: reports are grounded in the actual local test results, backend inspection, Render account inspection, and Codex CLI inspection; no external deployment or authentication was fabricated.
- Notes: the remaining blockers require authorized identity-provider configuration, backend changes, and a scoped deployment release.

### 2026-10-23 — Live production deployment audit

- Implemented: added the final live-deployment, OAuth, backend-auth, Render, Codex, ChatGPT, security, and beta-readiness reports.
- Files: `docs/PRODUCTION_DEPLOYMENT_REPORT.md`, `docs/OAUTH_VERIFICATION.md`, `docs/BACKEND_AUTH_INTEGRATION.md`, `docs/RENDER_SERVICE_STATUS.md`, `docs/CODEX_CONNECTION_TEST.md`, `docs/CHATGPT_CONNECTION_TEST.md`, `docs/SECURITY_TEST_RESULTS.md`, and `docs/CUSTOMER_BETA_READINESS.md`.
- Verification: the current Render CLI was checked once and returned an expired-token `401`; no deployment command was attempted. Local security and regression findings are separated from production-unverified checks.
- Notes: customer beta remains NO-GO until the owner reconnects Render, provisions OAuth/PKCE, and supplies the backend trust integration.

### 2026-10-23 — Live Render MCP deployment

- Implemented: committed and pushed the verified package, repaired the existing Render service from Python/Poetry to Docker, pinned the MCP SDK to the FastMCP-compatible major, configured public host validation, and registered the live endpoint in Codex.
- Files: `pyproject.toml`, `src/neyvro/remote_mcp.py`, and the live Render service configuration for `opengtmn-neyvro`.
- Verification: deployment `dep-dbd6p43bc2fs73a1eug0` is `live`; `https://opengtmn-neyvro.onrender.com/health` returned HTTP 200; external MCP initialize, `tools/list` (56), `resources/list`/read (35), `prompts/list` (35), and safe unauthenticated tool rejection passed. Codex registration succeeded.
- Notes: OAuth is still unsupported and backend adapter remains disabled, so private customer-data tools are not enabled. Codex and ChatGPT authenticated customer workflows remain unverified.

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
