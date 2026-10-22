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
