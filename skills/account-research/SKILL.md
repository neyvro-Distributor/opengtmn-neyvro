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
