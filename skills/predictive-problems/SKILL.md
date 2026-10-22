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
