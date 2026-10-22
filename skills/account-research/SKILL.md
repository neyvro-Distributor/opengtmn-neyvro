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
