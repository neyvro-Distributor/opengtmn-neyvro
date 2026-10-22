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
