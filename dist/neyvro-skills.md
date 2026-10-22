# Neyvro Agent Skills Bundle

This generated bundle is for explicit bulk import. Prefer registry discovery and on-demand loading in normal agent requests.


---

<!-- account-research/SKILL.md version 0.1.0 -->

---
name: account-research
description: Activate when researching a specific company or person before an authorized GTM decision, draft, or investigation.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read"]
related_skills: ["ideal-customer-profile","evidence","outreach-personalization"]
---

# account research

Collect relevant, dated, source-attributed company and buyer facts. Research requires Neyvro discovery services and must return evidence IDs, source URLs, observed timestamps, and uncertainty.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when researching a specific company or person before an authorized GTM decision, draft, or investigation.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.

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

<!-- cold-email-writing/SKILL.md version 0.1.0 -->

---
name: cold-email-writing
description: Activate when drafting or reviewing a personalized cold email or short sequence from authorized evidence.
version: 0.1.0
maturity: contract
mode: draft
required_scopes: ["intelligence:read","proposals:write"]
related_skills: ["account-research","outreach-personalization","email-deliverability"]
---

# cold email writing

Draft mode creates editable, evidence-linked variants with one clear ask. Sending or scheduling is external action requiring an approved proposal, mailbox permission, and idempotency key.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when drafting or reviewing a personalized cold email or short sequence from authorized evidence.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.

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

<!-- content-marketing-engine/SKILL.md version 0.1.0 -->

---
name: content-marketing-engine
description: Activate when planning buyer-question content, repurposing, distribution, or editorial measurement.
version: 0.1.0
maturity: contract
mode: knowledge
required_scopes: []
related_skills: ["positioning-and-messaging","seo-fundamentals","generative-engine-optimization"]
---

# content marketing engine

Explain topic selection, formats, cadence, and community norms. Neyvro has no content/social publishing backend; drafts are plans only.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when planning buyer-question content, repurposing, distribution, or editorial measurement.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.

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

<!-- discovery-and-qualification/SKILL.md version 0.1.0 -->

---
name: discovery-and-qualification
description: Activate when evaluating whether a company or contact is a qualified opportunity and preparing discovery questions.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read"]
related_skills: ["ideal-customer-profile","buyer-matching","predictive-problems"]
---

# discovery and qualification

Research may read authorized company, buyer, investigation, and pipeline context. Unknown is a valid result and must not become a positive score.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when evaluating whether a company or contact is a qualified opportunity and preparing discovery questions.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.

---

<!-- email-deliverability/SKILL.md version 0.1.0 -->

---
name: email-deliverability
description: Activate when assessing sending-domain readiness, authentication, reputation, pacing, bounce, or complaint risk.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read"]
related_skills: ["cold-email-writing","multichannel-sequences","outbound-metrics-and-benchmarks"]
---

# email deliverability

Research may inspect authorized mailbox and operation status. Draft mode produces remediation plans; it must not change DNS, mailbox settings, or send volume.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when assessing sending-domain readiness, authentication, reputation, pacing, bounce, or complaint risk.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.

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

<!-- generative-engine-optimization/SKILL.md version 0.1.0 -->

---
name: generative-engine-optimization
description: Activate when assessing or planning how a site or brand can be retrieved, quoted, and cited by AI answer engines.
version: 0.1.0
maturity: contract
mode: knowledge
required_scopes: []
related_skills: ["seo-fundamentals","content-marketing-engine","evidence"]
---

# generative engine optimization

Explain crawl access, answer-first content, entity authority, and measurement limits. Live research and publishing are blocked without a Neyvro provider.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when assessing or planning how a site or brand can be retrieved, quoted, and cited by AI answer engines.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.

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

<!-- ideal-customer-profile/SKILL.md version 0.1.0 -->

---
name: ideal-customer-profile
description: Activate when defining, refining, scoring, or reviewing an ideal customer profile, buyer roles, triggers, or anti-ICP.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read"]
related_skills: ["gtm-strategy","account-research","buyer-matching"]
---

# ideal customer profile

Turn onboarding and confirmed research context into explicit, filterable ICP criteria. Research requires authorized Neyvro onboarding/analysis data; writes preserve versioning and workspace ownership.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when defining, refining, scoring, or reviewing an ideal customer profile, buyer roles, triggers, or anti-ICP.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.

---

<!-- lead-sourcing-and-enrichment/SKILL.md version 0.1.0 -->

---
name: lead-sourcing-and-enrichment
description: Activate when finding or enriching ICP-fit companies and contacts with verified, source-labeled data.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read"]
related_skills: ["ideal-customer-profile","account-research","evidence"]
---

# lead sourcing and enrichment

Research requires authorized Neyvro providers and must preserve source, verification, freshness, and suppression states. Never guess an identity or email.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when finding or enriching ICP-fit companies and contacts with verified, source-labeled data.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.

---

<!-- linkedin-outreach/SKILL.md version 0.1.0 -->

---
name: linkedin-outreach
description: Activate when planning or reviewing compliant LinkedIn prospecting and relationship outreach.
version: 0.1.0
maturity: contract
mode: knowledge
required_scopes: []
related_skills: ["account-research","outreach-personalization","multichannel-sequences"]
---

# linkedin outreach

Provide safety-aware planning and drafts. Neyvro currently has no verified LinkedIn execution connector, so live research and external actions are blocked until an authorized provider contract exists.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when planning or reviewing compliant LinkedIn prospecting and relationship outreach.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.

---

<!-- multichannel-sequences/SKILL.md version 0.1.0 -->

---
name: multichannel-sequences
description: Activate when designing, reviewing, or operating a multi-step outreach cadence with explicit branch and stop logic.
version: 0.1.0
maturity: contract
mode: draft
required_scopes: ["proposals:write"]
related_skills: ["cold-email-writing","linkedin-outreach","reply-handling-and-objections"]
---

# multichannel sequences

Draft mode produces steps, timing, branches, suppression rules, and a proposed sequence. Launch, pause, resume, or send requires approval, provider permissions, and idempotent operations.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when designing, reviewing, or operating a multi-step outreach cadence with explicit branch and stop logic.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.

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

<!-- outbound-metrics-and-benchmarks/SKILL.md version 0.1.0 -->

---
name: outbound-metrics-and-benchmarks
description: Activate when measuring outreach funnels, setting denominators, comparing benchmarks, or diagnosing campaign health.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read"]
related_skills: ["email-deliverability","multichannel-sequences","revenue-attribution"]
---

# outbound metrics and benchmarks

Research may read authorized operations, mailbox, pipeline, and investigation metrics. Report denominators and data gaps; do not claim unsupported attribution.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when measuring outreach funnels, setting denominators, comparing benchmarks, or diagnosing campaign health.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.

---

<!-- outreach-personalization/SKILL.md version 0.1.0 -->

---
name: outreach-personalization
description: Activate when converting verified company or buyer evidence into relevant, non-creepy outreach personalization.
version: 0.1.0
maturity: contract
mode: draft
required_scopes: ["intelligence:read","proposals:write"]
related_skills: ["account-research","cold-email-writing","evidence"]
---

# outreach personalization

Create snippets tied to evidence IDs and mark uncertainty. Personal information must not be invented, inferred from sensitive traits, or copied without a source.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when converting verified company or buyer evidence into relevant, non-creepy outreach personalization.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.

---

<!-- positioning-and-messaging/SKILL.md version 0.1.0 -->

---
name: positioning-and-messaging
description: Activate when translating a product's differentiated value into positioning, message houses, or evidence-backed outreach angles.
version: 0.1.0
maturity: contract
mode: draft
required_scopes: ["intelligence:read"]
related_skills: ["gtm-strategy","ideal-customer-profile","cold-email-writing"]
---

# positioning and messaging

Use supplied or authorized brief evidence to draft positioning and messaging. Draft mode produces editable artifacts; external publishing or sending requires approval.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when translating a product's differentiated value into positioning, message houses, or evidence-backed outreach angles.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.

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

<!-- reply-handling-and-objections/SKILL.md version 0.1.0 -->

---
name: reply-handling-and-objections
description: Activate when classifying a prospect reply, drafting a response, or deciding whether follow-up must stop.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read","proposals:write"]
related_skills: ["cold-email-writing","discovery-and-qualification","multichannel-sequences"]
---

# reply handling and objections

Research requires authorized mailbox messages. Draft responses are reviewable; sending or changing follow-up state requires approval, mailbox permission, and idempotency.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when classifying a prospect reply, drafting a response, or deciding whether follow-up must stop.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.

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

<!-- seo-fundamentals/SKILL.md version 0.1.0 -->

---
name: seo-fundamentals
description: Activate when auditing or planning technical, on-page, content, or authority improvements for a website.
version: 0.1.0
maturity: contract
mode: knowledge
required_scopes: []
related_skills: ["generative-engine-optimization","content-marketing-engine"]
---

# seo fundamentals

Explain SEO audits and prioritization. Neyvro currently has no SEO crawler or publisher backend, so live research and external changes are blocked.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when auditing or planning technical, on-page, content, or authority improvements for a website.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.
