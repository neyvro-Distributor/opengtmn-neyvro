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

