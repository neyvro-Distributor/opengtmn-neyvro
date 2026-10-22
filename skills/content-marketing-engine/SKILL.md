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
