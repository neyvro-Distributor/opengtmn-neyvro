# Neyvro Agent Skills Bundle

This generated bundle is for explicit bulk import. Prefer registry discovery and on-demand loading in normal agent requests.


---

<!-- account-research/SKILL.md version 0.2.0 -->

---
name: account-research
description: Activate when researching a specific company or authorized buyer for a GTM decision, outreach draft, qualification review, or investigation; use existing Neyvro company-twin evidence before requesting new research.
license: MIT
metadata:
  version: 0.2.0
  maturity: playbook
  mode: research
  required_scopes: ["intelligence:read"]
  related_skills: ["ideal-customer-profile", "evidence", "outreach-personalization", "buyer-matching"]
---

# Account research

Produce a concise, cited account brief whose purpose is one evidence-backed outreach or GTM angle—not an unbounded dossier. Start with the most recent meaningful change (`why_now`), reuse fresh Neyvro company-twin research, and stop when the account-tier budget is spent.

## Operating modes

- **Knowledge-only:** explain research methods or provide a blank workflow without login, network calls, or claims about a real company.
- **Connected research:** use only authorized Neyvro read contracts. Prefer the company twin, verified evidence, signals, and timeline; request new research only for missing or stale fields.
- **Draft-only:** produce the brief and an outreach angle; never send, publish, enrich, or mutate CRM state.
- **External action:** requires an authenticated tenant scope, provider permission, explicit approval, audit logging, and an idempotency key.

If the requested company is not found, return `not_found` and research gaps. If access is not authorized, return `unauthorized` and do not infer or expose relationship history or private buyer data.

## Research workflow

1. Identify the company unambiguously using the authorized company ID or a verified domain. Do not silently merge similarly named companies.
2. Read the digital twin and existing timeline/evidence first. Treat a field as fresh only when its source-specific observation is inside the configured freshness window; do not repeatedly crawl fresh research.
3. Research in this order when permitted: business model and positioning; industry and approximate size; technology stack and changes; hiring and leadership; expansion and funding; product developments; public buyer information; authorized relationship history; open questions.
4. Prefer first-party or directly attributable sources. Attach `evidence_id`, source, observed timestamp, and confidence to every material observation.
5. Separate the brief into verified observations, reasonable inferences, predictions, unknown facts, and disqualifiers. Contradictory observations remain visible and lower confidence; they are not resolved by averaging or invention.
6. Select exactly one strongest outreach angle. It must be grounded in at least one recent verified signal plus a relevant product/ICP connection. If no such pair exists, return `angle_status: "not_ready"` instead of fabricating relevance.

## Account-tier budgets

Use the customer-approved tier when available. Otherwise report the missing tier and use the conservative C-tier budget.

| Tier | Maximum research budget | Minimum useful result |
| --- | ---: | --- |
| A | 15 minutes / 12 source fetches | one recent trigger, buyer context, and a cited angle |
| B | 5 minutes / 5 source fetches | one verified trigger or company-specific relevance line |
| C | 1 minute / 1 source fetch | role/industry/technology relevance only; no 1:1 deep research |

Budgets are limits, not targets. Reuse fresh verified evidence and stop early when the minimum result is met. Never use a personal or irrelevant detail as an outreach angle.

## Evidence rules

- `verified_observations`: directly supported, dated facts from authorized evidence.
- `inferences`: explicitly labeled conclusions supported by one or more observations.
- `predictions`: conditional hypotheses about likely priorities or timing; never state them as facts.
- `unknown_facts`: material fields not found or not fresh enough to rely on.
- `disqualifiers`: explicit ICP exclusions, access restrictions, contradictory identity, or evidence that makes the requested action unsuitable.
- A single signal does not qualify an account. Reconcile the account with the ICP and buyer context, and show negative evidence as well as supporting evidence.

## Required output

Return Markdown or JSON with exactly these core fields:

```json
{
  "status": "researched|stale|not_found|unauthorized|not_ready",
  "account_tier": "A|B|C|unknown",
  "why_this_company": "...",
  "why_now": "...",
  "relevant_buyers": [],
  "supporting_evidence": [],
  "negative_evidence": [],
  "verified_observations": [],
  "inferences": [],
  "predictions": [],
  "uncertainty": [],
  "unknown_facts": [],
  "disqualifiers": [],
  "recommended_next_action": "...",
  "outreach_angle": {"status": "ready|not_ready", "text": "...", "evidence_ids": []},
  "research_budget": {"minutes": 0, "source_fetches": 0, "used_fetches": 0},
  "freshness": {"last_researched_at": "...", "stale_fields": []}
}
```

`supporting_evidence` and `negative_evidence` must cite evidence IDs or source URLs. Do not manufacture company size, funding, hiring, technology, relationships, testimonials, results, or buyer identities. A recommendation may be a research question when evidence is insufficient.

## MCP integration contracts

Use these contracts only through an authenticated Neyvro adapter and the required `intelligence:read` scope. They are disabled by default when no adapter is configured:

- `neyvro_get_company_twin` — read the current tenant-scoped digital twin and freshness metadata.
- `neyvro_get_company_signals` — read verified technology, hiring, leadership, funding, expansion, and product signals.
- `neyvro_get_company_timeline` — read dated historical events without recrawling fresh sources.
- `neyvro_get_evidence` — retrieve cited evidence, confidence, provenance, and negative evidence.
- `neyvro_research_company` — request bounded research for missing/stale fields; this is a read/research operation, must honor the tier budget, and must not mutate CRM or send outreach.

The skill never creates a duplicate customer database. It consumes the existing company twin and returns a reviewable brief. Relationship history is included only when the adapter confirms authorization.

See also: `ideal-customer-profile` for fit, `evidence` for provenance, `outreach-personalization` for draft copy, and `buyer-matching` for persona selection.

---

<!-- buyer-matching/SKILL.md version 0.1.0 -->

---
name: buyer-matching
description: Activate when matching a target account or problem to buyer roles using authorized company and contact evidence.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read"]
related_skills: ["ideal-customer-profile","lead-sourcing-and-enrichment","discovery-and-qualification"]
---

# buyer matching

Separate role fit from verified identity and contactability. No person or email may be invented.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when matching a target account or problem to buyer roles using authorized company and contact evidence.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.

---

<!-- buying-windows/SKILL.md version 0.1.0 -->

---
name: buying-windows
description: Activate when assessing whether dated company changes create a timely, evidence-backed opportunity to investigate or propose outreach.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read"]
related_skills: ["company-changes","predictive-problems","buyer-matching","evidence"]
---

# buying windows

A trigger is an opportunity to investigate, not evidence that a buyer is ready. Outreach remains approval-gated.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when assessing whether dated company changes create a timely, evidence-backed opportunity to investigate or propose outreach.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.

---

<!-- cold-email-writing/SKILL.md version 0.2.0 -->

---
name: cold-email-writing
description: Activate when drafting or reviewing an evidence-grounded outbound email from an authorized opportunity, buyer, product, positioning, channel, and tone; this skill never sends messages.
license: MIT
metadata:
  version: 0.2.0
  maturity: playbook
  mode: draft
  required_scopes: ["intelligence:read", "proposals:write"]
  related_skills: ["account-research", "outreach-personalization", "email-deliverability", "multichannel-sequences"]
---

# Cold email writing

Create a short, reviewable outbound email with one clear ask. Relevance comes from Neyvro company and buyer evidence; the product message comes only from customer-approved positioning. This skill is draft-only: it must not send, schedule, publish, enroll, or mutate follow-up state.

## Required inputs

Require `opportunity_id`, `buyer_id`, `customer_product`, `approved_positioning`, `channel`, and `tone`. Read the buyer and opportunity through authorized Neyvro services when available. A draft may also receive verified prospect evidence, buyer role/name, company name, framework, and follow-up count. If a required input or evidence source is unavailable, return a flagged draft result rather than inventing it.

## Workflow

1. Confirm the buyer is not suppressed, opted out, an existing customer, or otherwise blocked. A suppressed recipient returns `approval_status: "blocked"` and no sendable body.
2. Select one relevant, recent, verified company signal. Trigger-first personalization is preferred; otherwise use a role/industry observation. Every concrete prospect claim must carry one or more evidence IDs and source metadata.
3. Form a business-relevant problem hypothesis as a question or conditional inference. Never state a business problem, funding event, technology migration, relationship, personal familiarity, result, or testimonial without evidence.
4. Translate only the approved positioning into one buyer-relevant value proposition. Do not add capabilities, metrics, customer names, or outcomes not present in the approved positioning.
5. Use exactly one framework per draft: PAS (problem–agitate–solution), BAB (before–after–bridge), AIDA (attention–interest–desire–action), or trigger-first. Keep the email short and plain-text friendly.
6. End with exactly one low-friction CTA. Follow-up variants are optional drafts and inherit the same evidence and suppression checks.
7. Run `neyvro_check_message_claims` before returning. Any unsupported, unverified, stale, or missing-evidence claim is flagged and prevents `draft_ready` status.

## Output contract

Return a structured result containing:

```json
{
  "opportunity_id": "opp-123",
  "buyer_id": "buyer-456",
  "framework": "trigger-first",
  "subject": "a question about the migration",
  "personalized_opener": {"text": "...", "evidence_ids": ["ev-1"]},
  "problem_hypothesis": {"text": "Could this change be creating ...?", "evidence_ids": ["ev-1"]},
  "value_proposition": {"text": "...", "evidence_ids": ["positioning-v2"]},
  "body": "...",
  "call_to_action": "Worth comparing notes?",
  "follow_up_variants": [],
  "evidence_ids": ["ev-1", "positioning-v2"],
  "flagged_claims": [],
  "approval_status": "draft_ready|needs_evidence|blocked",
  "send_allowed": false
}
```

`send_allowed` is always false. Claim flags must identify the text, reason, and missing or invalid evidence IDs. Approval status means ready for human review, not permission to send.

## Copy rules

- Subject: 1–6 plain words, relevant rather than hype-driven.
- Opener: one sentence about the recipient’s work, not generic praise or private personal details.
- Body: one problem hypothesis, one approved value proposition, and one CTA; avoid feature lists and multiple asks.
- Buyer-specific framing may differ for economic buyers, champions, users, technical evaluators, or approvers, but role assumptions must be marked as assumptions unless verified.
- Keep follow-ups shorter than the initial email and do not introduce a new claim without evidence.

## MCP contracts

- `neyvro_draft_email` — create a draft proposal from authorized opportunity, buyer, evidence, and approved positioning context.
- `neyvro_check_message_claims` — validate prospect and product claims, evidence links, suppression state, and approval readiness.
- `neyvro_get_email_draft` — retrieve an existing draft by exact identifier and version.

These contracts are draft/proposal operations only. Integrate with Neyvro follow-up and outreach services only for supported draft storage or review state; sending requires a separate approved action, mailbox permission, and idempotency key outside this skill.

See also: `account-research` for evidence, `outreach-personalization` for non-creepy relevance, `email-deliverability` for delivery controls, and `multichannel-sequences` for cadence design.

---

<!-- company-changes/SKILL.md version 0.1.0 -->

---
name: company-changes
description: Activate when detecting, explaining, or reviewing material changes in a target company's business context.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read"]
related_skills: ["digital-twins","evidence","buying-windows"]
---

# company changes

Research uses authorized monitoring and public-source evidence. Alerts or outreach proposals must name the evidence that triggered them.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when detecting, explaining, or reviewing material changes in a target company's business context.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.

---

<!-- content-marketing-engine/SKILL.md version 0.2.0 -->

---
name: content-marketing-engine
description: Activate when planning, drafting, repurposing, distributing, or measuring customer content from verified buyer questions, positioning, research, and approved brand voice; publishing always requires an authorized channel and explicit approval.
license: MIT
metadata:
  version: 0.2.0
  maturity: playbook
  mode: draft
  required_scopes: ["intelligence:read", "content:draft"]
  related_skills: ["positioning-and-messaging", "seo-fundamentals", "generative-engine-optimization", "evidence"]
---

# Content marketing engine

Build a sustainable, evidence-grounded content system that turns real buyer questions into useful content, then plans responsible distribution and measurement. Use Neyvro positioning, account research, product context, approved claims, and brand voice when available. This optional module does not require Neyvro login for knowledge-only planning or drafting from supplied inputs.

## Operating modes

- **Knowledge-only:** Explain content strategy, formats, topic clusters, channel norms, and measurement concepts without external calls or side effects.
- **Research:** Read authorized customer positioning, product, buyer, evidence, calendar, and outcome context. Return source IDs, freshness, confidence, assumptions, and gaps.
- **Draft-only:** Create topic ideas, briefs, articles, social adaptations, newsletters, and repurposing plans. Do not publish, schedule, or mutate a calendar.
- **External action:** Use only an explicitly authorized channel adapter, required scope, current approval, idempotency key, and audit record. If any condition is missing, return a proposal or blocked result.

## Workflow

1. Start with ICP buyer questions, sales or support language, approved positioning, product capabilities, and observed research gaps—not generic trends or invented demand.
2. Map each idea to audience, buyer stage, problem, format, evidence, intended outcome, and a topic cluster. Prefer a pillar asset with supporting pieces and a create-once-distribute-many plan.
3. Create an editorial brief before drafting: working title, question, audience, angle, outline, claims to verify, sources, CTA, brand voice, channel adaptations, owner, due date, and success measure.
4. Draft only supported claims. Mark unsupported claims for research or approval; never invent testimonials, customer results, audience engagement, publication status, or product capabilities.
5. Adapt for channel norms: useful professional insight on LinkedIn, give-first and disclosed participation on Reddit, concise opinion or threads on X, and deeper owned material in a website/blog or Substack. Never astroturf, seed repetitive promotion, buy engagement, or mass-post irrelevant content.
6. Reuse approved long-form material into shorter formats while preserving meaning, citations, caveats, and claim provenance. A derivative must not introduce a stronger claim than its source.
7. Measure only available observations. Separate observed engagement, subscribers, traffic, conversions, pipeline influence, and publication outcomes from unavailable or attributed metrics. Never infer a result from a draft or planned post.

## Content lifecycle

Every item has exactly one lifecycle state:

`DRAFT` -> `READY_FOR_REVIEW` -> `APPROVED` -> `SCHEDULED` -> `PUBLISHED`, with `FAILED` for an unsuccessful authorized operation. A draft or proposal cannot be represented as published. Missing approval, unsupported channel, stale claims, duplicate publication, or revoked permission blocks the transition.

## Required structured output

Return a reviewable object containing:

```json
{
  "ideas": [],
  "brief": null,
  "draft": null,
  "calendar": [],
  "repurposing": [],
  "distribution": [],
  "claim_review": {"supported": [], "needs_verification": [], "unsupported": []},
  "brand_voice": {"version": null, "status": "unknown"},
  "measurement": {"observed": [], "unavailable": [], "attribution_limits": []},
  "state": "DRAFT",
  "approval_required": true,
  "external_action_executed": false
}
```

Each claim has a source or is labeled `generic_product_messaging`. Each channel has authorization status, required permission, and whether publishing is supported. Calendar entries use deterministic IDs and reject duplicate publication keys.

## MCP contracts

- `neyvro_generate_content_ideas` — read customer context and produce evidence-linked ideas.
- `neyvro_create_content_brief` — create a reviewable brief without publishing.
- `neyvro_draft_content` — create or retrieve draft content with claim and voice checks.
- `neyvro_get_content_calendar` — read the authorized content calendar and publication history.
- `neyvro_propose_social_post` — create a social-post proposal; execution requires a separately authorized provider and approval.

These contracts are disabled without adapters. Supported adapters may include an authorized customer website/blog, X, Reddit, LinkedIn-assisted publishing, Substack, or other approved APIs. Unsupported channels are reported as unsupported; no browser automation or scraping is substituted.

## Safety and approval

- Publishing is never implied by drafting, approval is versioned, and the customer must explicitly approve the exact content, channel, audience, timing, and material claims.
- Recheck channel permission, recipient/community rules, suppression or opt-out constraints, duplicate publication key, and approval immediately before dispatch.
- Do not publish repetitive promotional community content. Respect platform rules, rate limits, disclosure requirements, robots/access controls, and customer brand voice.
- Never auto-merge, deploy, or silently change a website or repository. Repository or website changes are reviewable proposals only unless an authorized provider explicitly supports the approved operation.
- If a result cannot be verified, say `unknown` or `unavailable` and provide the research needed.

See `positioning-and-messaging` for approved product claims, `seo-fundamentals` and `generative-engine-optimization` for discoverability, and `evidence` for provenance.

---

<!-- continuous-investigation/SKILL.md version 0.1.0 -->

---
name: continuous-investigation
description: Activate when creating, monitoring, reviewing, assigning, or correcting a bounded Neyvro investigation.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read","proposals:write"]
related_skills: ["evidence","negative-evidence","company-changes","predictive-problems"]
---

# continuous investigation

Research uses Neyvro objectives, queues, workers, cases, and evidence. Every investigation needs bounded scope, retention, and an explicit stop condition.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when creating, monitoring, reviewing, assigning, or correcting a bounded Neyvro investigation.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.

---

<!-- digital-twins/SKILL.md version 0.1.0 -->

---
name: digital-twins
description: Activate when building or reviewing an evidence-backed, time-aware projection of a company, buyer, or opportunity.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read"]
related_skills: ["account-research","company-changes","evidence","negative-evidence"]
---

# digital twins

Research requires Neyvro company, investigation, and evidence services. A twin is a projection, not ground truth or proof of intent.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when building or reviewing an evidence-backed, time-aware projection of a company, buyer, or opportunity.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.

---

<!-- discovery-and-qualification/SKILL.md version 0.2.0 -->

---
name: discovery-and-qualification
description: Activate when qualifying an authorized sales opportunity or preparing a discovery-call brief using evidence, buyer research, conversation context, CRM records, and meeting history; never qualify from AI inference alone.
license: MIT
metadata:
  version: 0.2.0
  maturity: playbook
  mode: research
  required_scopes: ["intelligence:read"]
  related_skills: ["ideal-customer-profile", "buyer-matching", "predictive-problems", "reply-handling-and-objections"]
---

# Discovery and qualification

Prepare an evidence-backed account briefing and discovery plan. Use BANT for a fast first pass, MEDDIC for complex opportunities, and MEDDPICC when paper process and competition materially affect the deal. Framework fields are lenses for questions, not permission to infer budget, authority, need, timing, or purchase intent.

## Qualification workflow

1. Retrieve the opportunity, authorized company/buyer context, conversation thread, meeting history, existing CRM record, and opportunity evidence. Preserve tenant scope and source timestamps.
2. Separate `confirmed_facts`, `inferences`, `qualification_gaps`, and `conflicting_information`. Only verified, attributable evidence can populate confirmed facts.
3. Map the buying committee: economic buyer, champion, users, technical evaluator, procurement/legal, approver, and blockers. A title or AI guess is a stakeholder hypothesis until verified.
4. Assess pain severity and cost of inaction from the buyer’s own words or evidence. Treat an inferred pain as a discovery question, not a qualification fact.
5. Assess budget, timing, decision criteria/process, competition, and paper process only when explicitly supported. Never invent a budget, purchase timeline, authority, or commitment.
6. Apply disqualification rules: explicit no need, out-of-scope/anti-ICP, no permitted buyer path, suppression/opt-out, duplicate or wrong opportunity, or a customer-confirmed blocker. Record the evidence and do not override it with a predicted score.
7. Produce the brief, recommended questions, relevant objections, and one suggested next step. If CRM or meeting APIs are absent, keep the brief read-only and list the exact missing context.

## Framework lenses

- **BANT:** Budget, Authority, Need, Timeline. Unknown budget or timing stays unknown.
- **MEDDIC:** Metrics, Economic buyer, Decision criteria, Decision process, Identify pain, Champion.
- **MEDDPICC:** MEDDIC plus Paper process and Competition.

Select one primary framework and show the evidence status for every dimension. Do not aggregate unknowns into a positive score. A deal can be `qualified` only when the required dimensions for the selected framework are explicitly evidenced, the buyer path is credible, and no disqualifier or unresolved contradiction remains.

## Required output

```json
{
  "opportunity_id": "opp-123",
  "framework": "BANT|MEDDIC|MEDDPICC",
  "status": "qualified|incomplete|needs_review|nonbuyer|disqualified",
  "account_briefing": "...",
  "confirmed_facts": [],
  "qualification_dimensions": {"budget": {"status": "confirmed|unknown|conflicting", "evidence_ids": []}},
  "qualification_gaps": [],
  "conflicting_information": [],
  "buying_committee": [],
  "pain_severity": {"status": "confirmed|hypothesis|unknown", "evidence_ids": []},
  "relevant_objections": [],
  "recommended_discovery_questions": [],
  "suggested_next_step": "...",
  "research_gaps": [],
  "approval_status": "read_only|review_required",
  "send_allowed": false
}
```

`confirmed_facts` and each dimension’s evidence IDs must be source-attributed. A qualification status is not a forecast, win probability, or authorization to send. Discovery questions should resolve the highest-value gap first and must not presuppose a problem, budget, or timeline.

## MCP contracts

- `neyvro_get_opportunity_qualification` — read the current opportunity, qualification fields, evidence, CRM stage, and disqualifiers.
- `neyvro_generate_discovery_brief` — generate a versioned, read-only account briefing and question plan.
- `neyvro_get_buying_committee` — read authorized stakeholders, responsibilities, influence, and evidence.
- `neyvro_get_meeting_context` — read synchronized meeting notes, transcript summaries, and prior commitments when available.

These are read/planning contracts. If CRM or meeting APIs are missing, return `disabled`/`unknown` fields and preserve knowledge-only discovery guidance. No contract changes CRM qualification or sends a message.

See also: `ideal-customer-profile` for fit and disqualification, `buyer-matching` for roles, `account-research` for company evidence, and `reply-handling-and-objections` for conversation context.

---

<!-- email-deliverability/SKILL.md version 0.2.0 -->

---
name: email-deliverability
description: Activate when assessing authorized Gmail or Microsoft mailbox readiness, SPF/DKIM/DMARC configuration, sender limits, bounce or complaint risk, recipient hygiene, or safe email ramp-up; never change DNS or send mail.
license: MIT
metadata:
  version: 0.2.0
  maturity: playbook
  mode: research
  required_scopes: ["intelligence:read"]
  related_skills: ["cold-email-writing", "multichannel-sequences", "outbound-metrics-and-benchmarks"]
---

# Email deliverability

Assess sender safety from authorized mailbox/provider telemetry and explicitly reported DNS configuration. Deliverability is an operational health review, not a promise of inbox placement. Never invent scores, provider health, DNS records, or metrics.

## Operating modes

- **Knowledge-only:** explain SPF, DKIM, DMARC, pacing, list hygiene, bounce, complaint, and unsubscribe controls without login or external calls.
- **Connected read-only audit:** inspect authorized Gmail or Microsoft mailbox connection status, provider-reported limits/metrics, recipient verification, suppression, and any customer-authorized DNS evidence.
- **Draft-only remediation:** produce an editable checklist or ramp recommendation. Do not change DNS, mailbox settings, sender identity, limits, or sending volume.
- **External action:** test mail, DNS updates, mailbox changes, and sends require the relevant provider permission and explicit approval; this skill exposes no mutation or send operation.

## Audit sequence

1. Confirm the mailbox provider (`gmail` or `microsoft`), authorized connection, sender identity, sending domain, and tenant/workspace scope. A disconnected or unauthorized mailbox is `blocked` for sending readiness.
2. Check SPF, DKIM, and DMARC only from an authorized DNS check or customer-supplied record. If DNS access was not authorized, report `unknown`—do not perform a lookup or infer a pass.
3. Read provider-reported daily limits, sent count, remaining capacity, throttles, bounces, complaints, and unsubscribe events. Include the provider, observation time, and measurement window.
4. Check recipient hygiene before any proposed send: verified status, stale/unverified addresses, catch-all/risky addresses, opt-outs, suppression lists, repeated bounces, existing customers, and active follow-up stops.
5. Compare observed volume with the configured limit and ramp stage. Recommend gradual ramp-up and even pacing for new senders; warmup is guidance, never a guarantee of deliverability.
6. Return verified checks, provider health signals, best-practice recommendations, and unknown/unavailable metrics as separate sections. Use the most restrictive safe interpretation when a hard safety signal is present.

## Authentication guidance

| Check | Safe interpretation |
| --- | --- |
| SPF | One authoritative SPF record should authorize all actual sending services; missing, conflicting, or unverified is not ready. |
| DKIM | Signing should be enabled for the sending domain/provider; an unknown selector or unverified signature remains unknown. |
| DMARC | A published policy and aligned SPF/DKIM are required for a trustworthy configuration; report the observed policy without promising placement. |
| Sender identity | The authenticated mailbox and From identity must be authorized by the provider and workspace. |

Do not require direct DNS access when the customer has not authorized it. Never change DNS automatically. Do not send an external test message without approval.

## Safety thresholds and recommendations

Treat provider thresholds as authoritative when supplied; otherwise label benchmark guidance as a recommendation, not an observed result. Stop or review when daily limits are exceeded, repeated bounces rise, complaints occur, recipients are unverified, or suppression/opt-out state is uncertain. Honor unsubscribe and suppression immediately. Do not claim an inbox-placement percentage from bounce, open, or reply data.

## Required output

Return structured data with:

```json
{
  "status": "ready|review|blocked|unknown",
  "provider": "gmail|microsoft|unknown",
  "verified_configuration_checks": [],
  "provider_health_signals": [],
  "recommendations": [],
  "unknown_metrics": [],
  "recipient_safety": {"unverified": 0, "suppressed": 0, "repeated_bounces": 0},
  "sender_limits": {"daily_limit": null, "sent_today": null, "remaining": null},
  "authentication": {"spf": "verified|missing|failed|unknown", "dkim": "verified|missing|failed|unknown", "dmarc": "verified|missing|failed|unknown"},
  "send_allowed": false
}
```

Every observed check includes source, observed time, and provider where available. `send_allowed` is always false: this skill can inform another approved workflow but cannot send, warm up, schedule, or mutate configuration.

## Optional read-only MCP contracts

- `neyvro_get_mailbox_health` — Gmail/Microsoft connection, sender identity, authorization, and provider health.
- `neyvro_get_sender_limits` — provider limits, sent count, remaining capacity, throttles, and ramp state.
- `neyvro_get_delivery_metrics` — provider-reported bounce, complaint, unsubscribe, and delivery metrics with windows.
- `neyvro_audit_email_configuration` — authorized SPF/DKIM/DMARC and sender-configuration audit.

They are disabled without an authenticated adapter. Adapter setup requires a tenant-scoped Gmail or Microsoft connection, read-only provider permission, provider credential reference, and—only if DNS checks are requested—explicit customer authorization for DNS inspection. No credentials belong in skill files.

See also: `cold-email-writing` for copy, `multichannel-sequences` for cadence, and `outbound-metrics-and-benchmarks` for denominators and trend analysis.

---

<!-- evidence/SKILL.md version 0.1.0 -->

---
name: evidence
description: Activate when collecting, viewing, evaluating, correcting, or citing source-attributed evidence for Neyvro intelligence.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read","proposals:write"]
related_skills: ["account-research","company-changes","negative-evidence","continuous-investigation"]
---

# evidence

Evidence must retain source, observed time, subject, extraction context, and correction history. Missing evidence is not negative evidence unless explicitly classified.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when collecting, viewing, evaluating, correcting, or citing source-attributed evidence for Neyvro intelligence.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.

---

<!-- generative-engine-optimization/SKILL.md version 0.2.0 -->

---
name: generative-engine-optimization
description: Activate when assessing or improving an authorized website’s discoverability, answer-first content, entity clarity, structured data, AI-crawler access, freshness, or measurement plan for AI answer engines; never promise citations or fabricate visibility.
license: MIT
metadata:
  version: 0.2.0
  maturity: playbook
  mode: research
  required_scopes: ["intelligence:read", "proposals:write"]
  related_skills: ["seo-fundamentals", "content-marketing-engine", "evidence"]
---

# Generative engine optimization (GEO / AEO)

Help customers improve the chance that authorized, useful content is retrieved, understood, and cited by AI answer engines. GEO is non-deterministic: a single prompt, model response, or checklist score is not a visibility measurement. This optional module never changes a site automatically.

## Evidence hierarchy

Label recommendations by confidence:

- **Empirically supported / high confidence:** allow relevant crawlers, remove accidental access blocks, make important content server-rendered and answer-first, cite authoritative sources, keep claims factual, and maintain entity consistency.
- **Practical but directional:** self-contained answer blocks, clear headings, useful FAQs, named authors, visible dates, and relevant structured data improve parsing and user trust; citation lift is not guaranteed.
- **Emerging or disputed:** `llms.txt`, prompt-specific rewrites, composite GEO scores, and tactics claiming direct citation lift. Recommend only as bounded experiments, never as guarantees.

## Audit workflow

1. Confirm explicit website authorization and inspect AI/search crawler access, robots directives, WAF/edge responses, noindex/nosnippet directives, canonical URLs, and server-rendered content. A crawler restriction is an observed access issue, not a reason to invent visibility loss.
2. Review answer-first content: direct answer near the top, self-contained quotable statements, primary-source citations, clear definitions, question/intent coverage, and factual grounding.
3. Review structured data and entity consistency. Malformed schema, schema/text mismatch, conflicting organization names, stale descriptions, or inconsistent `sameAs`/canonical identity become findings with evidence.
4. Review authority indicators and freshness: named experts, primary sources, transparent authorship, visible publish/modified dates, reputable third-party references, and content updates that are real—not fake date bumps.
5. Recommend `llms.txt` only as an optional, emerging/disputed experiment. It must not outrank crawl access, useful content, authoritative sources, or ordinary SEO.
6. Build a measurement plan using a locked prompt set, repeated runs per engine, mention/citation rate, source share, and baseline-vs-after comparison. If no authorized visibility provider is integrated, return measurements as unavailable.

## Required output

```json
{
  "status": "complete|partial|blocked|unknown",
  "site": "https://example.com",
  "access_findings": [],
  "content_recommendations": [{"recommendation": "...", "evidence_level": "empirically_supported|directional|emerging_or_disputed", "priority": 1}],
  "schema_findings": [],
  "entity_consistency": [],
  "authority_indicators": [],
  "freshness_findings": [],
  "llms_txt": {"status": "present|missing|unknown", "recommendation": "optional experiment", "citation_guarantee": false},
  "visibility_measurements": {"status": "available|unavailable|conflicting", "provider": null, "data": null},
  "measurement_plan": [],
  "conflicting_findings": [],
  "unknowns": [],
  "repository_proposal": null,
  "merge_or_deploy_executed": false
}
```

Do not fabricate ChatGPT, Gemini, Claude, Perplexity, AI Overview, citation, mention, rank, or share-of-voice measurements. Do not claim `llms.txt` or schema markup guarantees citation. Every observation includes source and confidence; every recommendation states its evidence level.

## MCP contracts

- `neyvro_get_geo_audit` — read an authorized GEO audit and evidence.
- `neyvro_get_ai_visibility_findings` — read provider-reported visibility findings, or return unavailable when no provider is integrated.
- `neyvro_propose_geo_improvements` — create a reviewable repository PR/proposal when repository access is explicitly authorized.

These contracts are optional and disabled without an adapter. Repository proposals never auto-merge, deploy, publish, or silently modify a website. SEO remains a separate optional module.

See also: `seo-fundamentals` for classic technical SEO, `content-marketing-engine` for content planning, and `evidence` for provenance.

---

<!-- gtm-automation-with-chronos/SKILL.md version 0.1.0 -->

---
name: gtm-automation-with-chronos
description: Activate when a user asks to turn GTM planning into external execution through an authorized MCP or provider.
version: 0.1.0
maturity: contract
mode: execution
required_scopes: ["proposals:write","messages:send"]
related_skills: ["multichannel-sequences","cold-email-writing","lead-sourcing-and-enrichment"]
---

# gtm automation with chronos

Use Neyvro's capability registry and approval flow; OpenGTM's documented Chronos geo_* tools are not local Neyvro tools. Refuse execution when scope, provider, or approval is missing.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when a user asks to turn GTM planning into external execution through an authorized MCP or provider.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.

---

<!-- gtm-automation-with-neyvro/SKILL.md version 0.2.0 -->

---
name: gtm-automation-with-neyvro
description: Activate when coordinating Neyvro knowledge skills with connected customer intelligence, research, drafting, campaign, mailbox, conversation, meeting, SEO/GEO, content, or analytics services; use capability discovery and approval gates before any external action.
license: MIT
metadata:
  version: 0.2.0
  maturity: playbook
  mode: execution
  required_scopes: ["intelligence:read"]
  related_skills: ["gtm-strategy", "multichannel-sequences", "outbound-metrics-and-benchmarks", "evidence"]
---

# GTM automation with Neyvro

This is Neyvro’s native bridge between portable knowledge skills and authorized Neyvro MCP services. It does not require Chronos accounts, Chronos APIs, or `geo_*` tools. A Markdown skill remains useful without an account; this bridge discovers whether Neyvro can supply live context or execute an explicitly approved operation.

## Capability discovery

Before using connected data or proposing execution, call the capability contracts and determine:

- whether Neyvro is connected and authentication is valid;
- which scopes are granted and which are required;
- which services are implemented, unavailable, disabled, or blocked;
- which Gmail, Microsoft, social, website, repository, CRM, or other accounts are connected;
- which actions require customer approval and whether the exact approval is current;
- the tenant, freshness, provider, rate-limit, and data-quality boundaries.

Do not infer a connected account from a configured name, a skill description, or a documented tool. A service is available only when the server reports it available for the current tenant and scopes.

## Skill-to-capability map

Use metadata discovery first and load one exact skill on demand. The bridge map is maintained in `src/neyvro/gtm_automation.py`; it does not inject all skill documents into an agent request.

| Capability group | Portable skills | Neyvro-native tools |
|---|---|---|
| Customer strategy and ICP | `gtm-strategy`, `ideal-customer-profile`, `positioning-and-messaging` | `neyvro_get_customer_context`, `neyvro_get_gtm_strategy`, `neyvro_get_icp`, `neyvro_evaluate_icp_fit`, `neyvro_get_product_context`, `neyvro_get_positioning`, `neyvro_get_approved_claims` |
| Company research | `account-research`, `digital-twins`, `company-changes` | `neyvro_research_company`, `neyvro_get_company_twin`, `neyvro_get_company_signals`, `neyvro_get_company_timeline` |
| Monitoring and evidence | `evidence`, `negative-evidence`, `continuous-investigation` | `neyvro_get_evidence`, `neyvro_get_company_signals`, `neyvro_get_company_timeline`, `neyvro_get_investigation_status` |
| Predictive opportunities | `predictive-problems`, `buying-windows` | `neyvro_get_predictive_opportunities`, `neyvro_get_buying_windows`, `neyvro_get_opportunity_signals` |
| Buyer discovery | `buyer-matching`, `lead-sourcing-and-enrichment`, `discovery-and-qualification` | `neyvro_search_buyers`, `neyvro_get_opportunity_buyers`, `neyvro_get_opportunity_qualification`, `neyvro_get_buying_committee` |
| Contact enrichment | `lead-sourcing-and-enrichment` | `neyvro_enrich_contact`, `neyvro_get_contact_verification` |
| Message personalization | `outreach-personalization`, `linkedin-outreach` | `neyvro_get_personalization_context`, `neyvro_generate_personalization`, `neyvro_get_brand_voice`, `neyvro_get_linkedin_prospect_context` |
| Email drafting | `cold-email-writing`, `email-deliverability` | `neyvro_draft_email`, `neyvro_check_message_claims`, `neyvro_get_mailbox_health`, `neyvro_get_sender_limits` |
| Campaign proposals | `multichannel-sequences`, `content-marketing-engine` | `neyvro_create_campaign_draft`, `neyvro_propose_campaign`, `neyvro_create_content_brief`, `neyvro_propose_social_post` |
| Approved campaign execution | `multichannel-sequences`, `email-deliverability` | `neyvro_execute_approved_campaign`, `neyvro_get_campaign_status`, `neyvro_get_delivery_metrics` |
| Conversation intelligence | `reply-handling-and-objections` | `neyvro_get_conversation`, `neyvro_get_reply_status`, `neyvro_classify_reply`, `neyvro_get_followup_queue` |
| Meeting and pipeline intelligence | `discovery-and-qualification`, `revenue-attribution` | `neyvro_get_meeting_context`, `neyvro_get_opportunity_qualification`, `neyvro_get_pipeline_metrics`, `neyvro_get_revenue_attribution` |
| SEO/GEO analysis | `seo-fundamentals`, `generative-engine-optimization` | `neyvro_analyze_website`, `neyvro_get_seo_recommendations`, `neyvro_get_geo_audit`, `neyvro_get_ai_visibility_findings` |
| Content workflows | `content-marketing-engine` | `neyvro_generate_content_ideas`, `neyvro_create_content_brief`, `neyvro_draft_content`, `neyvro_get_content_calendar` |
| Analytics and revenue learning | `outbound-metrics-and-benchmarks`, `revenue-attribution` | `neyvro_get_campaign_metrics`, `neyvro_get_pipeline_metrics`, `neyvro_get_revenue_attribution`, `neyvro_get_signal_performance` |

The map is a routing contract, not proof that every service is currently implemented. The capability response must mark unavailable tools explicitly.

## Operating pattern

Coordinate work through:

`RESEARCH -> PLAN -> DRAFT -> REVIEW -> APPROVE -> EXECUTE -> VERIFY -> LEARN`

Knowledge-only work may stop after PLAN or DRAFT and remains useful while disconnected. Connected reads require valid authentication, tenant scope, and `intelligence:read`. Drafts and proposals never send, publish, schedule, change DNS, merge, deploy, or alter CRM state.

External execution requires all of the following at the server boundary:

1. a connected account and implemented service;
2. valid authentication and required scopes;
3. exact current approval for the action, content, recipients, channel, timing, and approval version;
4. eligibility, suppression, deliverability, and idempotency checks;
5. an audit record and post-action verification.

If any gate fails, return `disconnected`, `invalid_auth`, `insufficient_scope`, `pending_approval`, `unavailable`, or `blocked`. Never imply that a draft was sent or a proposal was executed.

## MCP contracts

- `neyvro_get_capabilities` — discover tenant-scoped service implementation and action support.
- `neyvro_get_connections` — discover connected accounts and provider health without exposing credentials.
- `neyvro_get_permissions` — discover granted scopes and permission expiry.
- `neyvro_get_approval_status` — verify an exact action’s current approval and version.

These are read-only discovery contracts. Execution uses the separately authorized service contract named in the capability response; this skill never substitutes an undocumented or Chronos tool.

## Disconnected behavior

When no Neyvro account is available, continue with knowledge-only strategy, ICP, research planning, copy drafts, briefs, deterministic campaign specifications, SEO/GEO recommendations, and measurement definitions from user-supplied context. Label live records, connected-account facts, execution results, and performance measurements as unavailable.

See the exact skill selected by metadata search for domain instructions; related skills are hints, not an instruction to load the entire library.

---

<!-- gtm-strategy/SKILL.md version 0.2.0 -->

---
name: gtm-strategy
description: Activate when selecting, reviewing, or refining a product's go-to-market motion, acquisition channels, or 30/60/90-day execution plan.
version: 0.2.0
maturity: playbook
mode: research
required_scopes: [intelligence:read, proposals:write]
related_skills: [ideal-customer-profile, positioning-and-messaging, account-research, outbound-metrics-and-benchmarks, content-marketing-engine]
---

# GTM strategy

Select the motion before writing campaign copy. Start with what Neyvro already
knows about the product, buyer, economics, industries, regions, and evidence.
Recommend one lead motion, at most one supporting motion for the first 90 days,
and explicitly deprioritize channels that do not fit the economics or buyer.

This skill works in two modes:

- **Knowledge-only:** explain the framework and produce a recommendation from
  facts supplied in the conversation. No login or MCP connection is required.
- **Connected:** read the customer's onboarding and confirmed ICP context using
  the Neyvro contracts below, then cite the returned evidence and research gaps.

Connected mode is disabled unless a real Neyvro adapter is present. Never invent
customer context, backend results, deal value, buyer intent, or channel results.

## 1. Build the customer context

Collect or retrieve the following before choosing a motion. Mark each field as
`observed`, `customer_stated`, `inferred`, `unknown`, or `blocked`.

| Area | Questions |
|---|---|
| Product | What is sold, to whom, what painful job it solves, time-to-value, implementation effort, and differentiator? |
| Economics | Typical contract/deal value, pricing unit, gross margin or delivery constraint, sales cycle, expansion potential, and acceptable acquisition cost? |
| Market | Which industries, company sizes, regions, regulations, and languages are in scope? Which are explicitly excluded? |
| Buyer | Economic buyer, champion, users, approvers, buying committee, and where each role learns or gathers trust? |
| Proof | Existing customers, outcomes, references, product usage, win/loss patterns, and evidence freshness? |
| Constraints | Team size, founder/sales capacity, budget, implementation capacity, compliance, and available integrations? |

If a number is missing, use a range only when the customer supplies a range;
otherwise add it to `research_gaps` and show how the recommendation depends on
it. Do not silently substitute a benchmark for customer data.

## 2. Estimate economics and fit

Use typical deal value rather than the maximum possible contract. If annual
value is available, call it ACV. If only monthly price is known, label the
calculation as an estimate and state churn/expansion assumptions.

| Signal | Strong fit | Default implication |
|---|---|---|
| Low value, low friction, fast time-to-value | Self-serve purchase is plausible | Lead with PLG and inbound; use outbound only for learning or high-value segments |
| Mid-market value and a defined buyer | Human guidance helps close | Lead with focused outbound plus a compounding inbound asset |
| High value, long cycle, multiple approvers, or compliance | Trust and orchestration matter | Lead with sales-led outbound/ABM; add partners or authority content selectively |
| Buyer already trusts an intermediary | Distribution is controlled by another party | Test partnerships before building a broad direct channel |

These are priors, not verdicts. A recommendation must explain which observed
facts moved the score and which unknowns could reverse it.

## 3. Compare the motions

Score each candidate against the customer's evidence, not generic enthusiasm.
Use `high`, `medium`, `low`, or `unknown` for fit and explain the reason.

### Outbound / sales-led

Fits when the ICP and buyer can be named, the contract value supports human
effort, a trigger or relevant angle exists, and the team can follow up. Prefer a
narrow account list, evidence-backed personalization, and a measurable sales
cycle over volume.

### Inbound / content / SEO / GEO

Fits when buyers search or ask about the problem, the company can publish
credible answers, and it can wait for compounding returns. It is usually a
supporting motion during the first 90 days unless existing demand is already
measurable.

### Product-led growth

Fits when activation is self-serve, time-to-value is short, the product can be
tried safely, and usage can create conversion or expansion. Do not recommend
PLG for a heavily customized, procurement-led implementation without naming the
missing product changes.

### Partnerships / channel

Fits when an integration, reseller, consultant, platform, or community already
owns trust and access to the buyer. Include partner incentive, enablement,
co-selling effort, and dependency risk; partnerships are not free distribution.

### Community / founder-led / social

Treat this as a channel layer, not automatically a lead motion. It fits when
the buyer gathers in a reachable community and the team can contribute useful
knowledge consistently without spam or platform-risk.

## 4. Select channels

Choose channels from the buyer's actual discovery and trust behavior:

- Named accounts and clear triggers: targeted email, calls, referrals, or
  carefully paced professional outreach.
- Searchable problem and educational proof: SEO, answer-first content, webinars,
  documentation, and selective GEO work.
- Fast self-serve value: product onboarding, templates, integrations, free or
  trial entry, lifecycle education, and product referrals.
- Intermediary-owned trust: integration marketplaces, agencies, consultants,
  resellers, and co-marketing.
- Founder/category education: useful community participation, events, and
  original research.

Low-priority channels are those with weak buyer access, poor economic fit,
unavailable capabilities, or unverified assumptions. Explain why they are low
priority and define the evidence that would promote them.

## 5. Plan crawl / walk / run

### Crawl — days 0–30

- One lead motion, one ICP segment, and one primary channel.
- Confirm product narrative, buyer role, trigger, proof, and baseline economics.
- Produce a small number of reviewed experiments with explicit stop conditions.
- Instrument replies, qualified conversations, activation, conversion, and cycle
  time according to the chosen motion.

### Walk — days 31–60

- Keep the first motion and add only one supporting channel or adjacent segment.
- Compare quality and economics against the crawl baseline.
- Review objections, disqualifiers, evidence freshness, and research gaps.
- Cut channels that consume capacity without producing a measurable learning or
  qualified outcome.

### Run — days 61–90

- Scale the repeatable motion within capacity limits.
- Add a second motion only when the first has a stable leading indicator and
  an owner, budget, and measurement plan.
- Formalize partner, content, lifecycle, or sales operations only when evidence
  supports the investment.

## 6. Output contract

Return a structured recommendation containing:

1. `recommended_motion` — one lead motion and optional supporting motion.
2. `reasons` — evidence-linked reasons, not generic advice.
3. `assumptions` — explicit estimates and their confidence.
4. `priority_channels` — owner, purpose, first experiment, and constraint.
5. `low_priority_channels` — rationale and promotion evidence.
6. `buyer_personas` — role, job, pain, buying influence, and evidence status.
7. `plan_30_60_90` — crawl, walk, and run actions with success gates.
8. `metrics` — leading and lagging measures with denominators.
9. `research_gaps` — missing facts that could change the decision.

If context is insufficient, return `recommended_motion: unknown`, a short
decision tree, and the smallest set of questions needed to decide. A confident
answer with fabricated customer facts is a failure.

## 7. Neyvro MCP integration contracts

These contracts are read/proposal interfaces only. The current repository does
not expose these endpoints, so connected execution stays disabled until a real
adapter is injected. The skill must work without them as a knowledge-only
advisor.

### `neyvro_get_customer_context`

```json
{
  "name": "neyvro_get_customer_context",
  "mode": "read",
  "required_scopes": ["intelligence:read"],
  "input": {"workspace_id": "uuid"},
  "output": {"status": "available|disabled|blocked", "context": {}, "evidence": [], "research_gaps": []}
}
```

Reads existing onboarding, product, sales, and confirmed ICP context. It must
not create a second customer database or accept a caller-supplied workspace ID
as proof of authorization.

### `neyvro_get_gtm_strategy`

```json
{
  "name": "neyvro_get_gtm_strategy",
  "mode": "read",
  "required_scopes": ["intelligence:read"],
  "input": {"workspace_id": "uuid", "version": "latest|uuid"},
  "output": {"status": "available|disabled|blocked", "strategy": {}, "evidence": [], "research_gaps": []}
}
```

Reads a stored, reviewed strategy if one exists. It must return `disabled` or
`blocked` rather than fabricate a strategy when no backend adapter exists.

### `neyvro_propose_gtm_strategy`

```json
{
  "name": "neyvro_propose_gtm_strategy",
  "mode": "proposal",
  "required_scopes": ["proposals:write"],
  "input": {"workspace_id": "uuid", "strategy": {}, "evidence_ids": [], "idempotency_key": "uuid"},
  "output": {"status": "proposed|disabled|blocked", "proposal_id": "uuid", "strategy": {}, "approval_required": true}
}
```

Creates a reviewable proposal only. It must not modify onboarding, ICP, CRM,
campaigns, or channels. Approval and persistence belong to the existing Neyvro
service once an adapter is implemented.

## Safety rules

- Never send, publish, launch, change DNS, change an ICP, or mutate a workspace
  from this skill.
- Never treat a prediction, trigger, benchmark, or generic framework as proof of
  buying intent.
- Keep connected reads tenant-scoped and evidence-attributed.
- Keep all external actions behind proposal, explicit approval, provider scope,
  audit logging, and idempotency.

## Related skills

Load these on demand, only when the recommendation needs them:

- `ideal-customer-profile` for account and buyer criteria.
- `positioning-and-messaging` for the narrative and proof.
- `account-research` for account-specific evidence.
- `outbound-metrics-and-benchmarks` for funnel measurement.
- `content-marketing-engine` for inbound/content execution planning.

---

<!-- ideal-customer-profile/SKILL.md version 0.2.0 -->

---
name: ideal-customer-profile
description: Activate when defining, refining, scoring, or reviewing an ICP, buyer personas, target-account filters, trigger events, or anti-ICP rules.
version: 0.2.0
maturity: playbook
mode: research
required_scopes: [intelligence:read, proposals:write]
related_skills: [gtm-strategy, account-research, evidence, buyer-matching, company-changes]
---

# Ideal Customer Profile (ICP)

An ICP describes the companies most likely to buy, succeed, retain, and expand.
It is narrower than the total addressable market. A persona describes the
people inside those companies. Use Neyvro's existing onboarding, confirmed ICP,
monitoring, company-intelligence, and opportunity evidence; do not create a
second customer database.

This skill works without login as a knowledge-only advisor. Connected reads are
disabled unless a real Neyvro adapter is injected. Customer-approved ICP settings
are never changed by evaluation or recommendation; changes are proposal-only and
require explicit authorization and approval.

## 1. Build the ICP from customer reality

Start from the existing onboarding and opportunity model:

1. Identify the product, customer problem, outcome, pricing unit, and delivery
   constraints.
2. Compare best customers with churned, lost, or poor-fit accounts.
3. Extract only attributes that can be observed or filtered: industry, size,
   geography, technology, buyer role, problem, and trigger.
4. Record the source, date, confidence, and whether each attribute is observed,
   customer-stated, inferred, unknown, or blocked.
5. Keep the initial ICP to 3–6 high-signal criteria; place exploratory signals in
   a research backlog rather than quietly widening the target.

Do not derive the ICP from closed-won revenue alone. Retention, expansion,
time-to-value, support burden, implementation effort, and disqualification
patterns are equally important.

## 2. Firmographic and market criteria

Return explicit filters, ranges, and exclusions:

| Dimension | Examples | Required treatment |
|---|---|---|
| Industry | security, healthcare, fintech, manufacturing, SaaS | Use normalized industry names or codes; list excluded industries and why |
| Company size | employees, revenue, locations, business model | Use ranges; mark missing employee/revenue data as unknown |
| Geography | country, region, timezone, language, regulatory regime | Separate serviceable regions from researched regions |
| Company type | B2B/B2C, public/private, startup/enterprise, agency/competitor | Define anti-ICP types explicitly |
| Economics | budget, ACV, buying committee, implementation capacity | Never infer budget from brand size alone |

A company is not a fit because it is large, famous, or in a target country.
Those are at most one dimension in the scorecard.

## 3. Technographic criteria

Model the technology as a filterable set:

- required technologies: absence is a mismatch or research gap;
- complementary technologies: positive fit when verified;
- migration technologies: relevant when a transition creates the problem;
- excluded technologies: anti-ICP or implementation incompatibility;
- unknown stack: do not treat as a match.

Technology signals must be source-attributed. Examples of useful signals include
cloud expansion, migration from a legacy platform, security tooling changes, and
new infrastructure ownership. A named technology without a source is an
assumption, not evidence.

## 4. Buyer personas and customer problems

Separate the account from the people:

| Persona field | Output |
|---|---|
| Role and seniority | economic buyer, champion, user, approver, blocker |
| Job to be done | what the person must accomplish |
| Problem | operational or business problem and cost of inaction |
| Buying influence | decision, budget, implementation, security, procurement |
| Evidence | source, freshness, confidence, and unknowns |

Map each ICP problem to the buyer role that experiences it and the evidence that
shows it exists. Do not call a company qualified just because a target title
appears in a directory; buyer-role evidence and company-fit evidence must be
evaluated together.

## 5. Trigger events and monitoring

Use recent, attributable triggers to prioritize timing, not to prove intent.
Neyvro monitoring/company intelligence may look for:

- technology migration;
- cloud expansion;
- new security requirements or compliance deadlines;
- engineering or security hiring;
- funding or budget expansion;
- leadership changes;
- product launches;
- relevant M&A, outages, public pain, or competitor change.

Every trigger must include source, observed date, subject, confidence, and an
expiry/freshness rule. One trigger alone never qualifies a company. It can
increase priority only when the underlying firmographic, technology, buyer, or
problem criteria are also corroborated.

## 6. Weighted fit scorecard

Use a transparent 0–100 score. Default weights are adjustable only through an
authorized ICP proposal:

| Dimension | Default weight |
|---|---:|
| Industry | 20 |
| Company size/economics | 15 |
| Geography | 10 |
| Technology | 15 |
| Buyer role | 15 |
| Problem | 15 |
| Trigger | 10 |

For each dimension use match, mismatch, or unknown. Award a dimension's
weight only when the match is supported by evidence. Suggested tiers:

- A — 80–100: prioritize now after checking disqualifiers and contactability.
- B — 60–79: nurture or research; do not assume buying intent.
- C — 0–59: low priority or skip for now.
- Disqualified: hard anti-ICP rule; never promote because of a high score.
- Incomplete: insufficient corroboration or evidence; not qualified.

A company may be qualified only when:

1. score is at least 60;
2. at least two independent dimensions match;
3. at least two evidence records support those dimensions;
4. no hard exclusion is present; and
5. required information is not materially unknown.

This prevents a single signal, such as funding or hiring, from being presented as
customer qualification.

## 7. Anti-ICP and disqualification rules

Define hard exclusions before sourcing:

- excluded industries, geographies, company types, or regulatory regimes;
- competitors, partners that cannot buy, or existing customers handled elsewhere;
- too small to afford or support the product;
- implementation environment that cannot use the product;
- prohibited jurisdictions or unsupported languages;
- students, job seekers, personal projects, or free-email-only targets where
  they cannot become legitimate customers;
- explicit suppression, opt-out, privacy, or ownership-removal state.

A hard exclusion returns disqualified even when other dimensions match.
Unknown returns incomplete, not disqualified, unless policy explicitly defines
the missing fact as a required exclusion check.

## 8. Evidence-backed refinement

Refine the ICP only from aggregated outcomes and reviewed evidence:

- compare A/B/C conversion, retention, expansion, cycle time, and support burden;
- review false positives, false negatives, losses, churn, and disqualifications;
- identify which criteria predicted a positive outcome and which were vanity;
- propose weight, range, inclusion, exclusion, or trigger changes;
- attach evidence IDs and show the before/after effect;
- require customer approval before changing the stored ICP version.

The evaluation operation is read-only. neyvro_propose_icp_changes creates a
reviewable proposal and must not mutate approved settings.

## 9. Output contract

Return:

- icp_version and a concise ICP summary;
- firmographic, technographic, size, geography, buyer, problem, and trigger
  criteria;
- industry/geography/company-type exclusions and anti-ICP rules;
- weighted scorecard and A/B/C thresholds;
- buyer personas mapped to problems and evidence;
- search specification with filterable fields;
- assumptions and confidence;
- monitoring signals and freshness rules;
- research gaps;
- for a company evaluation: score, tier, status, matched dimensions, missing
  dimensions, disqualifiers, reasons, and evidence.

When the data is incomplete, return recommended_motion: unknown, a short
decision tree, and the smallest set of questions needed to decide. Never
fabricate a company attribute, buyer, technology, trigger, or qualification.

## 10. Neyvro MCP contracts

These are safe service contracts, not claims that endpoints currently exist in
this repository. Without an adapter, return disabled and no fabricated data.

### neyvro_get_icp

Input: { "workspace_id": "uuid", "version": "latest|uuid" }

Output: { "status": "available|disabled|blocked", "icp": {}, "evidence": [], "research_gaps": [] }

Reads the existing customer-approved ICP and onboarding/opportunity context. It
must enforce workspace authorization and never create a duplicate customer
record.

### neyvro_evaluate_icp_fit

Input: { "workspace_id": "uuid", "company_id": "uuid", "evidence_ids": [] }

Output: { "status": "available|disabled|blocked", "fit": {}, "evidence": [], "research_gaps": [] }

Reads authorized company-intelligence and monitoring evidence, then evaluates
the stored ICP without changing it. A single signal must never produce
qualified.

### neyvro_propose_icp_changes

Input: { "workspace_id": "uuid", "changes": {}, "evidence_ids": [], "idempotency_key": "uuid" }

Output: { "status": "proposed|disabled|blocked", "proposal_id": "uuid", "approval_required": true }

Creates a versioned review proposal. It cannot update customer-approved ICP
settings, onboarding answers, opportunity records, or monitoring rules without
a separate authorized approval flow.

## Behavior modes and safety

- Knowledge-only: explain ICP design and scorecard use with supplied facts; no
  Neyvro login or MCP is required.
- Research: read tenant-scoped onboarding, company intelligence, monitoring, and
  opportunity evidence; return provenance and gaps.
- Draft-only: produce a proposed ICP or fit evaluation; do not persist it.
- External action: only propose changes through the approval contract; never
  source, message, enroll, or mutate customer settings directly.

Load related skills on demand, not automatically: gtm-strategy for motion fit,
account-research for account evidence, evidence for provenance, and
buyer-matching for role-level research.

---

<!-- lead-sourcing-and-enrichment/SKILL.md version 0.2.0 -->

---
name: lead-sourcing-and-enrichment
description: Activate when selecting ICP-fit accounts, finding buyer roles, or enriching authorized business contacts with deduplicated, provenance-labeled, verified data.
license: MIT
metadata:
  version: 0.2.0
  maturity: playbook
  mode: research
  required_scopes: ["intelligence:read"]
  related_skills: ["ideal-customer-profile", "account-research", "evidence", "buyer-matching", "email-deliverability"]
---

# Lead sourcing and enrichment

Turn an approved ICP into a clean, reviewable buyer list. Select accounts first, infer roles second, then enrich contacts through a bounded waterfall. A discovered person is not automatically a reachable lead: identity, company match, provenance, verification, freshness, permitted use, suppression, and entitlement must all be explicit.

## Operating modes

- **Knowledge-only:** explain sourcing, verification, or list-hygiene methods without login, provider calls, or real-person claims.
- **Connected research:** read authorized ICP, company, opportunity, CRM, suppression, and provider results. Return unknowns when a service is unavailable.
- **Draft-only:** produce a proposed target list or enrichment plan. Never create a CRM record, enroll a sequence, or send a message.
- **External action:** requires tenant scope, provider permission, customer entitlement, usage budget, explicit approval, audit logging, and an idempotency key.

## Discovery workflow

1. Apply the customer-approved ICP to companies. Exclude existing customers, active opportunities, suppressed accounts, competitors, and accounts with a disqualifier before searching for people.
2. Infer the buying committee from the problem and approved persona model: economic buyer, champion, user, technical evaluator, approver, and blocker. Role inference is a hypothesis until a source verifies the current role.
3. Match existing CRM and opportunity contacts before paying a provider. Reuse a fresh authorized contact record; do not create duplicates for a changed title or alternate spelling.
4. Use a waterfall from the lowest-cost authorized source to the next provider. Stop after a verified hit or when the customer budget/rate limit is exhausted. Paid enrichment is disabled without explicit entitlement and remaining usage budget.
5. Verify company identity and current employment together. A contact from a similarly named or former company is a `wrong_company` exclusion, not a usable match.
6. Verify email separately from identity. `verified` means the provider or verification service confirmed the address; a guessed/pattern-generated address is never verified. Catch-all, unknown, risky, invalid, bounced, and unverified states remain non-verified.
7. Normalize and deduplicate by provider person ID, normalized email, and `(name, company domain, current role)` fallback. Preserve all source references and the strongest verification history.
8. Check global/workspace suppression, opt-outs, existing-customer exclusions, and permitted-use constraints before returning a contact. Never expose private personal data or scrape a platform against its rules.

## Contact contract

For every discovered person return:

```json
{
  "name": "Alex Morgan",
  "company": "Example Inc",
  "current_role": "VP Engineering",
  "buyer_category": "economic_buyer|champion|user|technical_evaluator|approver|blocker|unknown",
  "source": {"provider": "crm|provider-name", "record_id": "...", "url": "..."},
  "verification_status": "verified|unverified|catch_all|invalid|stale|opted_out|wrong_company",
  "last_verified_at": "2026-10-20T00:00:00Z",
  "opportunity_ids": ["opportunity-123"],
  "contact_details": {
    "email": "alex@example.com",
    "email_provenance": "provider_verified|crm_verified|pattern_guess|unknown",
    "permitted_use": true,
    "permitted_use_basis": "workspace policy or provider terms"
  }
}
```

Email and phone fields require source, observed time, verification result, and permitted-use basis. A pattern guess may be returned only as `unverified` when the workflow explicitly allows it; never use it as proof of identity or deliverability.

## Budgets, freshness, and failure behavior

- Track `provider_calls`, `paid_calls`, `units_consumed`, `units_remaining`, and per-provider rate-limit state.
- Do not call a paid provider if `entitled` is false, the usage budget is exhausted, or the provider has no permitted-use basis.
- Default contact freshness is 30 days unless the customer or provider supplies a stricter window. A stale record must be re-verified or marked `stale`; it must not silently become current.
- Provider timeout, quota, auth, policy, or malformed-response failures are recorded as provider events and do not become guessed data. Continue to the next authorized waterfall step only when its budget and policy allow.
- Opt-outs and suppression are hard stops. Existing customers and active opportunities are excluded by default; a customer-approved exception must be explicit and auditable.

## MCP contracts

Use authenticated, tenant-scoped adapters with `intelligence:read`:

- `neyvro_search_buyers` — search ICP-filtered accounts and buyer roles.
- `neyvro_get_opportunity_buyers` — read existing opportunity contacts and relationship context.
- `neyvro_enrich_contact` — run bounded waterfall enrichment; paid calls require entitlement and usage budget.
- `neyvro_get_contact_verification` — read verification, freshness, provenance, opt-out, and permitted-use state.

The skill prefers existing Neyvro buyer/CRM services and does not create a duplicate contact database. Provider adapters must use approved B2B APIs or first-party CRM data, respect provider terms, and never scrape prohibited platforms.

## Structured result

Return `accounts_considered`, `accounts_excluded`, `contacts`, `duplicates_removed`, `suppressed_contacts`, `provider_events`, `usage`, and `research_gaps`. Include a sample result even in knowledge-only mode, with fictional values clearly marked as examples. A contact is eligible for downstream outreach only when `verification_status` is `verified`, `permitted_use` is true, and no suppression or existing-customer exclusion applies.

See also: `ideal-customer-profile` for fit, `account-research` for account signals, `buyer-matching` for role hypotheses, and `email-deliverability` for sending controls.

---

<!-- linkedin-outreach/SKILL.md version 0.2.0 -->

---
name: linkedin-outreach
description: Activate when researching an authorized professional profile, selecting a relevant LinkedIn outreach angle, drafting a connection note or direct message, or recording customer-confirmed manual outreach; never automate LinkedIn actions.
license: MIT
metadata:
  version: 0.2.0
  maturity: playbook
  mode: draft
  required_scopes: ["intelligence:read", "proposals:write"]
  related_skills: ["account-research", "outreach-personalization", "multichannel-sequences", "cold-email-writing"]
---

# LinkedIn outreach

Assist compliant professional relationship outreach using verified company and buyer evidence. LinkedIn is an assisted channel in Neyvro: research permitted context, draft, review, open the profile, let the customer act manually, and record the customer-confirmed action.

## Supported workflow

1. Read an authorized prospect profile, company context, current role, relationship state, and dated professional evidence. Cross-tenant IDs are non-disclosing `not_found`/`forbidden` results.
2. Check profile freshness and current-role evidence. If the profile is missing, stale, unauthorized, or provider-restricted, report the gap rather than guessing.
3. Select one work-relevant angle: a verified company change, a verified professional post or stated responsibility, or an authorized relationship context. Avoid sensitive personal traits, private details, generic praise, and manufactured familiarity.
4. Draft one of: a pitch-free connection note, a short direct message for an existing relationship, or a meaningful engagement suggestion tied to a verified post. Keep each claim linked to evidence IDs.
5. Require customer review and approval. The customer opens the profile and manually performs the action on LinkedIn. Record only a customer-confirmed action and its timestamp.
6. For relationship-aware follow-up, read the recorded relationship state and stop when the prospect declined, opted out, or no longer has a verified current role. Never infer acceptance, reply, or relationship status from an attempted draft.

## Explicitly unsupported

Neyvro must not build or use unauthorized scraping, browser-account hijacking, cookie-based bots, stealth automation, prohibited bulk connection requests, automated DMs, automated comments/reactions, or any capability that violates LinkedIn or provider terms. Direct send/connection/comment tools are unsupported unless an officially authorized platform capability is later supplied and separately approved. Never fabricate execution, delivery, acceptance, or engagement.

## Draft outputs

Return structured drafts such as:

```json
{
  "status": "draft_ready|needs_evidence|stale|missing_profile|unsupported|blocked",
  "prospect_id": "person-123",
  "action": "connection_note|direct_message|engagement_suggestion",
  "message": "...",
  "engagement_suggestion": null,
  "angle": "...",
  "evidence_ids": ["ev-1"],
  "flagged_claims": [],
  "relationship_state": "not_connected|pending|connected|unknown",
  "approval_status": "review_required|blocked|unsupported",
  "manual_steps": ["Review draft", "Open profile", "Customer acts manually", "Record confirmed action"],
  "external_action_executed": false
}
```

Connection notes should be brief and non-pitchy. A direct message should be drafted only when relationship context permits it; otherwise return a connection-note suggestion. Engagement should add a real professional observation, not a disguised sales pitch. One soft ask maximum, and no automated follow-up.

## MCP contracts

- `neyvro_get_linkedin_prospect_context` — read tenant-scoped professional profile, company, role, permitted posts, evidence, and freshness.
- `neyvro_draft_linkedin_message` — create a reviewable connection-note, DM, or engagement draft; it does not send or publish.
- `neyvro_get_social_relationship` — read authorized connection, prior interaction, opt-out, and follow-up state.
- `neyvro_record_manual_outreach` — record an action only after the customer confirms they manually performed it; it does not call LinkedIn.

All contracts require an authorized adapter and tenant scope. If a provider is unavailable, return `disabled` with setup requirements. Provider setup must use officially authorized platform capabilities and permitted data providers; credentials, cookies, and session tokens never belong in skills or logs.

See also: `account-research` for company evidence, `outreach-personalization` for relevance, `multichannel-sequences` for reviewable cadence, and `cold-email-writing` for email alternatives.

---

<!-- multichannel-sequences/SKILL.md version 0.2.0 -->

---
name: multichannel-sequences
description: Activate when designing, reviewing, compiling, or operating a customer-approved multichannel outreach sequence with deterministic timing, branches, eligibility checks, and stop rules.
license: MIT
metadata:
  version: 0.2.0
  maturity: playbook
  mode: draft
  required_scopes: ["intelligence:read", "proposals:write"]
  related_skills: ["cold-email-writing", "linkedin-outreach", "email-deliverability", "reply-handling-and-objections"]
---

# Multichannel sequences

Design a declarative campaign specification and compile it into a deterministic state machine. Sequence planning and compilation are safe local operations; actual sending must use a separately authorized Neyvro campaign/follow-up backend after explicit customer approval.

## Declarative campaign specification

Each step must define all of these fields:

```json
{
  "step_id": "step-1",
  "channel": "email|linkedin_assisted|authorized_social",
  "recipient": {"buyer_id": "buyer-1", "company_id": "company-1"},
  "sender": {"mailbox_id": "mailbox-1", "identity": "sales@example.com"},
  "message": {"draft_id": "draft-1", "content": "reviewed content"},
  "scheduled_time": "2026-10-24T09:00:00Z",
  "preconditions": ["sender_available", "recipient_eligible", "approval_current"],
  "stop_conditions": ["reply", "unsubscribe", "hard_bounce", "meeting_booked", "customer_cancelled"],
  "approval_version": "approval-v1"
}
```

Only data-defined channels, preconditions, stop conditions, and branch targets are accepted. Never compile or execute arbitrary LLM-generated code. Unsupported channels are rejected or marked `unsupported`; they are never silently treated as email.

## Campaign lifecycle

The compiler and runtime support exactly these states:

`DRAFT → PROPOSED → PENDING_APPROVAL → APPROVED → SCHEDULED → RUNNING → COMPLETED`

Any running campaign may enter `PAUSED`, `CANCELLED`, or `FAILED`. Approval revocation, sender unavailability, recipient ineligibility, provider failure, or an operator pause must prevent dispatch. Approval is versioned; a step approved under an old version cannot run under a new or revoked version.

## Required safety rules

- Stop immediately after a genuine reply, unsubscribe/opt-out, hard bounce, meeting booking, or customer cancellation.
- Recheck sender availability, mailbox permission, recipient eligibility, suppression, current approval version, and channel capability immediately before every dispatch.
- Deduplicate jobs with a deterministic campaign/step/recipient key. Concurrent reply events are idempotent; the first stop event wins and later dispatches are rejected.
- A paused campaign schedules no new work. Resume requires a fresh authorized state transition and eligibility recheck.
- LinkedIn and social steps are assisted unless an officially authorized provider capability exists. Draft/open-profile/manual-action paths must not become automated sends.
- Scheduling must use provider timezone and customer-approved windows; do not assume a local timezone.

## Structured output

Return the declarative spec, compiled state machine, deterministic job IDs, branch/exit rules, approval version, current campaign state, and warnings. Draft/proposal outputs are reviewable and do not send. A send-capable backend must report provider, approval, idempotency, and operation status.

## MCP contracts

- `neyvro_create_campaign_draft` — validate and persist a draft specification.
- `neyvro_propose_campaign` — submit a versioned campaign for customer approval.
- `neyvro_get_campaign` — read the exact campaign specification and version.
- `neyvro_pause_campaign` — request an approved pause/stop through the existing campaign service.
- `neyvro_get_campaign_status` — read state, stop reason, jobs, provider health, and approval version.

Use Neyvro’s existing campaign and follow-up implementation where available. If scheduler integration is absent, return a deterministic schedule plan and `disabled` adapter status; do not create a second sending engine. Sending, scheduling on a live provider, resuming, and cancellation must remain behind the separately authorized approval/idempotency boundary.

See also: `cold-email-writing` for email drafts, `linkedin-outreach` for assisted social steps, `email-deliverability` for sender safety, and `reply-handling-and-objections` for reply-driven stops.

---

<!-- negative-evidence/SKILL.md version 0.1.0 -->

---
name: negative-evidence
description: Activate when recording, evaluating, or explaining disconfirming evidence, missing signals, or reasons not to act.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read","proposals:write"]
related_skills: ["evidence","predictive-problems","continuous-investigation"]
---

# negative evidence

Separate absence, unknown, and contradiction. Never claim “not found” means “does not exist.”

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when recording, evaluating, or explaining disconfirming evidence, missing signals, or reasons not to act.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.

---

<!-- outbound-metrics-and-benchmarks/SKILL.md version 0.2.0 -->

---
name: outbound-metrics-and-benchmarks
description: Activate when analyzing outbound funnel performance, campaign health, attribution, or contextual benchmarks using Neyvro campaign, conversation, and CRM records; every metric must expose its numerator, denominator, time window, segment, and data limitations.
license: MIT
metadata:
  version: 0.2.0
  maturity: playbook
  mode: research
  required_scopes: ["intelligence:read"]
  related_skills: ["cold-email-writing", "email-deliverability", "multichannel-sequences", "linkedin-outreach", "reply-handling-and-objections"]
---

# Outbound metrics and benchmarks

Measure the outbound funnel from sourced contacts through revenue using real, tenant-authorized Neyvro campaign, conversation, mailbox, opportunity, CRM, and cost records. Treat analytics as descriptive unless an experiment or valid causal design supports a stronger conclusion.

## Metric contract

Every returned metric must include:

```json
{
  "metric": "positive_reply_rate",
  "numerator": 0,
  "denominator": 0,
  "rate": null,
  "unit": "ratio",
  "time_window": {"start": "...", "end": "..."},
  "segment": {},
  "sample_size": 0,
  "status": "available|unavailable|insufficient_sample|inconsistent",
  "definition": "unique positive human replies / unique delivered outreach attempts",
  "source_event_ids": [],
  "limitations": []
}
```

Use unique event or entity IDs. Do not count duplicate webhooks twice. A zero denominator yields `rate: null` and `status: unavailable`, never zero. A metric with missing CRM outcomes is unavailable or partial, not a fabricated zero.

Canonical funnel definitions:

- `contacts_found`: unique contacts discovered in the window.
- `contact_verification_rate`: unique contacts with a verified status / unique contacts found.
- `outreach_attempts`: unique authorized send attempts, grouped by campaign and channel.
- `delivery_rate`: unique delivered attempts / unique outreach attempts.
- `bounce_rate`: unique bounced attempts / unique outreach attempts; distinguish hard and soft bounce when available.
- `reply_rate`: unique human replies / unique delivered attempts; exclude automatic replies when classification is available.
- `positive_reply_rate`: unique positive human replies / unique delivered attempts; also report positive share of human replies separately.
- `meetings_booked_rate`: unique meetings booked / unique outreach attempts, plus meetings / positive replies when possible.
- `qualified_opportunity_rate`: unique qualified opportunities / unique outreach attempts; qualification requires CRM evidence, not inference alone.
- `pipeline_value`: sum of authorized opportunity amounts created in the window, with currency and missing-value counts.
- `won_outcomes` and `lost_outcomes`: unique CRM outcomes recorded in the window, with unknown outcomes separated.
- `revenue_attribution`: revenue attached by the customer’s declared attribution model; report model and attribution uncertainty.
- `cost_per_qualified_opportunity`: authorized campaign and provider cost / unique qualified opportunities; unavailable when cost or qualified-opportunity denominator is missing.

## Segmentation and data quality

Allow filters for customer/tenant, ICP segment, industry, signal type, buyer role, campaign, sending channel, sender identity, and time period. Apply tenant filtering before aggregation. Never expose another tenant’s events through a blended benchmark or error message.

Report duplicate IDs, impossible event order, conflicting delivery/reply states, missing CRM opportunity outcomes, unknown currency, stale records, and cross-system mismatches as warnings. A reply without a delivered or sent event is inconsistent unless the provider explicitly supplies the missing history. Preserve raw event provenance and the IDs used in each numerator and denominator.

## Benchmarks and recommendations

External benchmarks are contextual ranges only. They must include source, population, date, denominator, channel, and applicability limitations; never present them as Neyvro targets or guarantees. Do not manufacture a benchmark when no source is supplied.

Use meetings booked, qualified opportunities, pipeline, and revenue as the primary success measures. Reply and positive-reply rates are useful leading indicators. Open rates are directional deliverability diagnostics only and must not be the primary KPI or an A/B winner criterion.

Tie recommendations to observed performance and sample size: identify the lowest trustworthy funnel stage, state whether the sample is sufficient, suggest targeting/copy/list/deliverability/follow-up investigation, and distinguish correlation from causal impact. A segment difference is correlation unless randomized treatment, a credible quasi-experiment, or another causal design is documented.

## MCP contracts

- `neyvro_get_campaign_metrics` — read tenant-authorized campaign, delivery, reply, and meeting events.
- `neyvro_get_pipeline_metrics` — read CRM opportunity stages, amounts, qualification, and outcomes.
- `neyvro_get_revenue_attribution` — read customer-configured attribution and attached revenue.
- `neyvro_get_signal_performance` — compare authorized signal types and segments against downstream outcomes.

These contracts are disabled without real adapters. They must return source freshness, scope, time window, segment, and data-quality warnings. No contract invents CRM outcomes or backend records.

## Required result

Return `metrics`, `definitions`, `segments`, `data_quality`, `benchmarks`, `recommendations`, `causal_limits`, `time_window`, and `tenant_scope`. Include `open_rate_note` stating that opens are not the primary success metric. Never claim revenue attribution, campaign lift, or causal impact when the required records or design are unavailable.

See `multichannel-sequences` for campaign state, `email-deliverability` for sending safety, `reply-handling-and-objections` for reply classification, and `evidence` for provenance.

---

<!-- outreach-personalization/SKILL.md version 0.2.0 -->

---
name: outreach-personalization
description: Activate when turning authorized company, buyer, opportunity, positioning, and brand-voice context into evidence-linked personalization snippets at strategic, qualified, or lightweight effort levels; never send messages.
license: MIT
metadata:
  version: 0.2.0
  maturity: playbook
  mode: draft
  required_scopes: ["intelligence:read", "proposals:write"]
  related_skills: ["account-research", "cold-email-writing", "linkedin-outreach", "ideal-customer-profile"]
---

# Outreach personalization

Create reusable, channel-neutral snippets that make outreach relevant without pretending familiarity. Use customer-approved positioning, digital-twin state, verified company signals, buyer responsibilities, opportunity hypotheses, authorized relationship history, and approved brand voice. This skill drafts and validates only; it never sends messages.

## Effort levels

| Level | Use when | Required personalization |
| --- | --- | --- |
| High-touch strategic | A-tier or strategic opportunity | verified trigger, why-now context, buyer responsibility, pain hypothesis, approved benefit, proof, and one CTA |
| Medium-touch qualified | ICP-fit account with bounded research | one verified company signal, role-relevant hypothesis, approved benefit, and one CTA |
| Lightweight relevant | volume or low-information account | generic product messaging plus verified role/industry framing; no invented account claim |

Effort controls research and copy depth; it never lowers evidence or authorization standards. If evidence is insufficient for the selected level, downgrade the output or return `needs_evidence`.

## Snippet categories

Return swappable snippets for:

- `verified_trigger` — one current, source-linked company change;
- `why_now` — why the change may make the conversation timely, clearly labeled as an inference;
- `relevant_pain_hypothesis` — a conditional, buyer-role-specific hypothesis, never a stated fact without evidence;
- `product_benefit` — approved positioning or clearly labeled generic product messaging;
- `proof_point` — approved, source-linked proof only;
- `call_to_action` — one low-friction ask, without a guarantee.

Every non-generic snippet carries `evidence_ids`, source references, observed time, and confidence. Generic product messaging is labeled `generic: true` and must not be presented as prospect personalization.

## Workflow and guardrails

1. Read the authorized customer positioning, brand voice, company twin/signals, buyer responsibilities, opportunity hypothesis, and relationship history. Keep tenant and recipient scope intact.
2. Select at most one strongest current trigger. Contradictory signals remain visible, lower confidence, and block a trigger claim until resolved.
3. Match the angle to the buyer’s verified role and responsibilities. If the evidence concerns another role, mark `buyer_role_mismatch` and do not use it as individualized copy.
4. Separate observation, inference, generic product material, and proof. Never fabricate familiarity, compliments, personal details, outcomes, customer results, guarantees, or product capabilities.
5. Avoid identical bodies across recipients. A reusable category is acceptable; the individualized trigger or role framing must differ when the account has distinct evidence. If no evidence differs, return generic messaging instead of fake personalization.
6. Validate all snippets with `neyvro_validate_outreach_claims`. The result is reviewable draft material, never a send authorization.

## Structured output

```json
{
  "effort_level": "high_touch_strategic|medium_touch_qualified|lightweight_relevant",
  "snippets": [{"category": "verified_trigger", "text": "...", "evidence_ids": ["ev-1"], "generic": false, "confidence": 0.9}],
  "confidence_limitations": [],
  "evidence_links": [{"evidence_id": "ev-1", "source": "...", "observed_at": "..."}],
  "flagged_claims": [],
  "brand_voice": {"status": "consistent|unknown|flagged", "applied": "..."},
  "approval_status": "draft_ready|needs_evidence|blocked",
  "send_allowed": false
}
```

## MCP contracts

- `neyvro_get_personalization_context` — read tenant-scoped positioning, digital-twin signals, buyer responsibilities, opportunity hypothesis, authorized relationship history, and brand voice.
- `neyvro_generate_personalization` — generate versioned reviewable snippets for a selected effort level.
- `neyvro_validate_outreach_claims` — validate evidence links, role fit, contradictions, generic labels, and brand-voice constraints.
- `neyvro_get_brand_voice` — read the customer-approved voice and version.

These contracts require an authorized adapter and never send. Integrate with cold email, LinkedIn-assisted, or sequence workflows only by passing reviewable draft snippets; external action remains separately approval-gated.

See also: `account-research` for signals, `cold-email-writing` for email composition, `linkedin-outreach` for assisted social use, and `ideal-customer-profile` for buyer fit.

---

<!-- positioning-and-messaging/SKILL.md version 0.2.0 -->

---
name: positioning-and-messaging
description: Activate when developing, reviewing, or refining product positioning, value propositions, battlecards, buyer messaging, or approved message-house claims.
version: 0.2.0
maturity: playbook
mode: draft
required_scopes: [intelligence:read, proposals:write]
related_skills: [gtm-strategy, ideal-customer-profile, account-research, cold-email-writing]
---

# Positioning and messaging

Positioning is the context that makes a product's value clear to a specific
buyer. Messaging is how that context is expressed. Start with Neyvro's existing
onboarding answers, product documents, approved positioning, approved claims,
and evidence. Do not create a duplicate product database.

This skill works as a knowledge-only advisor when Neyvro is disconnected. In
connected mode it reads authorized product context and approved claims. Drafts
are reviewable; positioning, claims, brand voice, and external messages are not
changed without an authorized proposal and approval.

## 1. Build the product and category context

Collect and label:

- product name, category, buyer, user, and job to be done;
- documented capabilities and constraints;
- real competitor alternatives, including manual work, spreadsheets,
  in-house systems, delay, or doing nothing;
- customer problems in the customer's language;
- target industries, use cases, and buyer personas;
- approved brand voice and words to prefer or avoid;
- approved claims, proof points, sources, dates, and version;
- unknowns and claims requiring review.

Use a market category the buyer recognizes and can budget for. If category,
capability, or problem information is missing, say so. Do not fill gaps with
generic product marketing language and do not infer a capability from a product
name.

## 2. Positioning components

Work through these five components:

1. Competitive alternatives: what the buyer actually does without the product,
   and where each alternative wins.
2. Unique capabilities: documented capabilities that are meaningfully different
   from the alternatives.
3. Value: what the capability changes for the buyer, expressed as a problem or
   outcome rather than a feature.
4. Target persona: the buyer role that cares most about the value, plus users,
   champions, approvers, and blockers.
5. Category: the frame that helps the buyer understand what the product is.

A feature is not differentiation until it explains a meaningful advantage against
a real alternative. Be honest about where the alternative wins.

## 3. Before / after / bridge

Use this structure:

- Before: the customer's current painful state, supported by customer language or
  evidence.
- After: the better state the product can credibly enable; label the outcome as a
  hypothesis when proof is absent.
- Bridge: the product's documented capabilities, kept brief.

Lead with the buyer's outcome, not a feature list. Never turn an unapproved
capability into a promise.

## 4. Value proposition and message house

Return:

- a one-line value proposition: product category plus buyer-relevant outcome;
- three message pillars;
- one reason-to-believe or proof point under each pillar;
- the caveat or unsupported claim under each pillar;
- buyer-specific variants for the economic buyer, champion, user, approver, and
  blocker where context supports them;
- objection-aware reframes that acknowledge where alternatives may win.

A message house is not a license to manufacture proof. If a pillar has no
approved proof, mark it as a research gap and keep the language conditional.

## 5. Differentiation and battlecards

For each named alternative, create a compact battlecard:

| Field | Requirement |
|---|---|
| Alternative | confirmed competitor, manual process, or status quo |
| Buyer reason | why the buyer chooses it today |
| Neyvro difference | documented capability and relevant buyer value |
| Where the alternative wins | honest tradeoff |
| Proof | approved claim/source or explicit missing proof |
| Reframe | one respectful, non-defamatory response |
| Do not claim | unsupported weakness or superiority |

Never manufacture competitor weaknesses, customer results, testimonials, market
share, certifications, or product capabilities. If competitor information is
unverified, identify it as an information gap rather than a weakness.

## 6. Buyer-specific messaging

For each persona, map:

- role and buying influence;
- job and pain;
- desired outcome;
- message angle;
- evidence/proof;
- likely objection;
- honest response;
- next safe action.

Use the customer's approved brand voice. If no voice is approved, use clear,
specific, restrained language and mark voice as unconfirmed. Do not impersonate
a customer or claim that a persona said something they did not say.

## 7. Objection-aware messaging

Handle objections by acknowledging the buyer's current alternative first:

- “We already use a spreadsheet” → explain the documented gap the product closes;
- “Our team can build this” → compare maintenance, ownership, and evidence only
  when those facts are approved;
- “We do not need this yet” → state the trigger or cost hypothesis and ask for
  validation, not urgency theater;
- “We need proof/security review” → return approved proof or identify exactly
  what evidence is missing.

No objection response may introduce a new unsupported claim.

## 8. Versioning and approval

Every generated positioning artifact returns a version and approval status:

- draft: generated from supplied facts and not approved;
- needs_approval: contains unsupported claims, missing proof, unconfirmed voice,
  or changed positioning;
- approved: only when the connected source contains an approved version and
  every surfaced claim is within approved claims;
- blocked: a required authorized source or approval is unavailable.

Reading approved positioning is safe. Proposing changes is not persistence.
Customer-approved positioning and claims must remain unchanged until a customer
authorized proposal is approved by the existing Neyvro service.

## 9. Structured output

Return exactly these top-level fields:

- positioning_summary: category, one-liner, before/after/bridge, and version;
- target_persona: role, influence, evidence status, and buyer-specific context;
- problem_statement: problem, cost/impact hypothesis, and evidence;
- differentiation: documented capabilities, real alternatives, honest tradeoffs,
  and battlecards;
- proof_points: approved claims and sources only;
- message_angles: persona-specific, objection-aware draft angles;
- unsupported_claims: every capability, outcome, comparison, or proof that cannot
  be safely stated as fact;
- approval_status: draft, needs_approval, approved, or blocked.

Also include assumptions, research gaps, brand-voice status, and evidence IDs
inside the relevant objects. If product information is incomplete, return a
useful framework with explicit gaps instead of inventing content.

## 10. Neyvro MCP contracts

These are safe adapter contracts. The current repository does not expose these
endpoints, so connected functionality remains disabled until a real adapter is
injected.

### neyvro_get_product_context

Input: { "workspace_id": "uuid" }

Output: { "status": "available|disabled|blocked", "product_context": {}, "evidence": [], "research_gaps": [] }

Reads existing onboarding, product documents, and approved workspace context. It
must enforce tenant authorization and must not create a duplicate product record.

### neyvro_get_positioning

Input: { "workspace_id": "uuid", "version": "latest|uuid" }

Output: { "status": "available|disabled|blocked", "positioning": {}, "version": "string", "approval_status": "string", "evidence": [] }

Reads a versioned approved or draft positioning artifact without changing it.

### neyvro_propose_positioning

Input: { "workspace_id": "uuid", "positioning": {}, "evidence_ids": [], "idempotency_key": "uuid" }

Output: { "status": "proposed|disabled|blocked", "proposal_id": "uuid", "version": "string", "approval_required": true }

Creates a versioned review proposal only. It must not mutate approved
positioning, claims, brand voice, onboarding, CRM, or outbound messages.

### neyvro_get_approved_claims

Input: { "workspace_id": "uuid", "version": "latest|uuid" }

Output: { "status": "available|disabled|blocked", "claims": [], "version": "string", "evidence": [] }

Reads the allowlist of claims that may be stated as fact. No approved claim may
be silently edited or widened by this skill.

## Behavior modes and safety

- Knowledge-only: teach positioning and produce conditional drafts from supplied
  facts; no login or MCP is required.
- Research: read tenant-scoped product documents, positioning, claims, and
  evidence; return provenance and gaps.
- Draft-only: create a reviewable message house, battlecards, and persona
  variants; do not publish or send.
- External action: use only the proposal contract and require explicit approval,
  audit logging, provider scope, and idempotency.

Load related skills on demand: gtm-strategy for motion fit,
ideal-customer-profile for target accounts, account-research for evidence, and
cold-email-writing for channel-specific copy.

---

<!-- predictive-problems/SKILL.md version 0.1.0 -->

---
name: predictive-problems
description: Activate when identifying or reviewing likely future business problems from current evidence and patterns.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read"]
related_skills: ["company-changes","evidence","discovery-and-qualification","buying-windows"]
---

# predictive problems

Research may read investigations and prediction outputs. Predictions are advisory and never proof of intent, budget, or purchase.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when identifying or reviewing likely future business problems from current evidence and patterns.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.

---

<!-- reply-handling-and-objections/SKILL.md version 0.2.0 -->

---
name: reply-handling-and-objections
description: Activate when retrieving and classifying an authorized email reply, drafting an objection-aware response, or stopping follow-up after a reply, rejection, unsubscribe, meeting, or out-of-office event.
license: MIT
metadata:
  version: 0.2.0
  maturity: playbook
  mode: research
  required_scopes: ["intelligence:read", "proposals:write"]
  related_skills: ["cold-email-writing", "multichannel-sequences", "discovery-and-qualification"]
---

# Reply handling and objections

Connect Gmail/Microsoft message synchronization and the existing Neyvro follow-up module to a thread-aware reply workflow. The first safe action on any genuine reply is to stop incompatible automatic follow-up before another step can execute. Reading, drafting, and sending are separate permissions; this skill never sends automatically.

## Reply taxonomy

Classify each inbound message into exactly one category:

`INTERESTED`, `REQUEST_INFORMATION`, `NOT_NOW`, `OBJECTION`, `REFERRAL`, `WRONG_PERSON`, `NOT_INTERESTED`, `UNSUBSCRIBE`, `OUT_OF_OFFICE`, `MEETING_REQUEST`, or `UNKNOWN`.

Keep the raw message, thread ID, conversation ID, sender, received time, classifier confidence, evidence/span, and classification version. A duplicate webhook is idempotent. A message from the wrong email thread or tenant is not classified against the campaign.

## Workflow

1. Retrieve the authorized conversation and full thread context. Verify tenant ownership, mailbox provider, sender/recipient identity, thread ID, and campaign/follow-up association.
2. Atomically mark the matching follow-up queue stopped or paused before classification-driven drafting. This guard runs for every genuine reply, including out-of-office and unknown replies.
3. Classify the reply with structured evidence and confidence. Safety-critical `UNSUBSCRIBE` and explicit `NOT_INTERESTED` states immediately suppress future outreach and require no further automated contact.
4. Return a suggested next action: human review, meeting proposal, information draft, referral routing, reminder after a stated out-of-office return date, objection response, or stop/suppress.
5. Draft only after classification and human-review rules permit it. Objection responses acknowledge once, reframe briefly, and ask one next step; do not argue repeatedly. Meeting suggestions use only authorized sender availability and never invent times.
6. Recheck follow-up stop state, suppression, thread, tenant, and approval immediately before any separately authorized send service could act.

## Category actions

- `INTERESTED` / `MEETING_REQUEST`: human review plus a concise meeting suggestion using available times or an approved booking link.
- `REQUEST_INFORMATION`: provide one relevant approved resource, then one soft next-step question.
- `OBJECTION`: acknowledge, address once with approved evidence, and offer one small next step.
- `NOT_NOW`: record the requested timing as a reviewable reminder; do not continue the active cadence.
- `REFERRAL` / `WRONG_PERSON`: thank the sender and request or route to the named responsible person, subject to authorization.
- `NOT_INTERESTED` / `UNSUBSCRIBE`: stop and suppress immediately; no draft is required for unsubscribe.
- `OUT_OF_OFFICE`: stop the active cadence and retain only the provider-return date/alternate that is explicitly present.
- `UNKNOWN`: stop incompatible automation and require human review; never guess intent.

## Structured output

```json
{
  "conversation_id": "conv-1",
  "thread_id": "thread-1",
  "reply_id": "msg-9",
  "category": "INTERESTED",
  "confidence": 0.94,
  "classification_evidence": [{"span": "yes, Thursday works", "source": "msg-9"}],
  "followup_stop": {"required": true, "status": "stopped", "reason": "reply_detected"},
  "suppression": {"required": false, "status": "unchanged"},
  "suggested_next_action": "human_review_meeting_times",
  "draft": null,
  "approval_status": "review_required",
  "send_allowed": false
}
```

## MCP contracts and permissions

- `neyvro_get_conversation` — read tenant-scoped Gmail/Microsoft conversation and thread context.
- `neyvro_get_reply_status` — read classification, stop state, suppression, and processing/idempotency state.
- `neyvro_classify_reply` — classify an authorized inbound reply and apply the stop-on-reply guard.
- `neyvro_draft_reply` — create a human-reviewable objection or meeting response; no send.
- `neyvro_get_followup_queue` — read the current follow-up queue and stopped/paused tasks.

Read contracts require `intelligence:read`; classification/queue stop and draft persistence require the appropriate proposal/follow-up permission; sending belongs to a separate `messages:send` service with explicit approval, mailbox permission, and idempotency key. If Gmail/Microsoft sync or follow-up persistence is unavailable, return `disabled`/`blocked` and do not fabricate a message or stop confirmation.

See also: `cold-email-writing` for copy, `multichannel-sequences` for stop rules, and `discovery-and-qualification` for next-step questions.

---

<!-- revenue-attribution/SKILL.md version 0.1.0 -->

---
name: revenue-attribution
description: Activate when linking evidence and approved GTM actions to pipeline or revenue outcomes with explicit attribution limits.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read"]
related_skills: ["outbound-metrics-and-benchmarks","continuous-investigation","evidence"]
---

# revenue attribution

Distinguish correlation, influence, and verified revenue attribution. Do not mutate CRM or claim causal revenue impact without a defined model and complete event data.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when linking evidence and approved GTM actions to pipeline or revenue outcomes with explicit attribution limits.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.

---

<!-- seo-fundamentals/SKILL.md version 0.2.0 -->

---
name: seo-fundamentals
description: Activate when auditing an explicitly authorized website for technical SEO, crawlability, indexing, metadata, headings, internal links, content relevance, page experience, mobile readiness, or structured data; this optional module never deploys or merges changes.
license: MIT
metadata:
  version: 0.2.0
  maturity: playbook
  mode: research
  required_scopes: ["intelligence:read", "proposals:write"]
  related_skills: ["generative-engine-optimization", "content-marketing-engine", "evidence"]
---

# SEO fundamentals

Provide an actionable, source-attributed SEO audit for a customer-authorized website. Keep SEO optional so unavailable crawling, Search Console, repository, or performance data never blocks core company intelligence or GTM workflows.

## Audit workflow

1. Validate the URL and authorization scope. Accept only `http`/`https` URLs the customer authorized; do not crawl inaccessible, private, or unrelated hosts.
2. Read robots directives and provider rate limits before fetching. Respect disallowed paths, crawl budgets, redirects, authentication boundaries, and partial-crawl limits. A blocked page is an access result, not a guessed issue.
3. Inspect available HTML and headers for crawlability/indexing, title and meta description, canonical, heading hierarchy, internal links, image alt text, content relevance, mobile viewport, HTTPS, page-experience signals, and JSON-LD/structured data.
4. Separate observations from recommendations. Every issue includes URL/page source, observed value, severity, confidence, and why it matters. Missing Search Console/ranking/traffic/Core Web Vitals data remains `unknown`; never invent performance or search rankings.
5. Prioritize by impact, confidence, effort, and implementation dependency. Include a verification checklist with the evidence needed to confirm each fix.
6. If repository changes are requested, create only a reviewable proposal or pull request through authorized repository access. Never merge, deploy, edit DNS, or publish automatically.

## Audit areas

- **Technical:** robots.txt, sitemap discoverability, status codes, redirects/chains, canonical URLs, HTTPS, crawl errors, index directives, JavaScript dependency.
- **On-page:** unique title, meta description, one logical H1, H2/H3 hierarchy, descriptive URLs, internal linking, image alt text.
- **Content relevance:** search intent, topic coverage, useful/people-first content, freshness only when dates are observed, authorship and primary-source signals.
- **Experience/mobile:** viewport, responsive signals, page-weight/latency observations only when actually measured, mobile rendering, intrusive elements.
- **Structured data:** valid-looking JSON-LD presence/type and required-field gaps; do not promise rich results.

## Required output

```json
{
  "status": "complete|partial|blocked|invalid_url|inaccessible",
  "site": "https://example.com",
  "crawl": {"pages_requested": 10, "pages_analyzed": 7, "partial": true, "robots_respected": true, "rate_limit_events": []},
  "observations": [],
  "issues": [{"id": "seo-1", "area": "metadata", "severity": "high|medium|low|unknown", "url": "...", "observation": "...", "evidence": [], "confidence": 0.9}],
  "recommendations": [{"issue_id": "seo-1", "improvement": "...", "priority": 1, "effort": "low|medium|high", "verification": "..."}],
  "unknown_metrics": ["rankings", "organic traffic", "Core Web Vitals"],
  "verification_checklist": [],
  "repository_proposal": null,
  "merge_or_deploy_executed": false
}
```

## MCP contracts

- `neyvro_analyze_website` — run a bounded, authorized, robots-aware website analysis.
- `neyvro_get_seo_recommendations` — retrieve or prioritize recommendations from an audit.
- `neyvro_propose_seo_changes` — create a reviewable repository proposal/PR only when repository authorization exists.

These contracts are optional and disabled without an authorized adapter. Repository proposals require explicit repository access and review permissions; merge and deploy are unsupported. Do not require direct repository or DNS access for an audit.

See also: `generative-engine-optimization` for answer-engine discoverability and `content-marketing-engine` for content planning.
