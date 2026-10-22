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
