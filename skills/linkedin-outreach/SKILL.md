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
