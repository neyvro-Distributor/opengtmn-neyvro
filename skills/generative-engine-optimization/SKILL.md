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
