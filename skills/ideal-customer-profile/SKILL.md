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
