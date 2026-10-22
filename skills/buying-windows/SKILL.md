---
name: buying-windows
description: Activate when assessing whether dated company changes create a timely, evidence-backed opportunity to investigate or propose outreach.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read"]
related_skills: ["company-changes","predictive-problems","buyer-matching","evidence"]
---

# buying windows

A trigger is an opportunity to investigate, not evidence that a buyer is ready. Outreach remains approval-gated.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when assessing whether dated company changes create a timely, evidence-backed opportunity to investigate or propose outreach.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.
