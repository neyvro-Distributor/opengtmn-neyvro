---
name: continuous-investigation
description: Activate when creating, monitoring, reviewing, assigning, or correcting a bounded Neyvro investigation.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read","proposals:write"]
related_skills: ["evidence","negative-evidence","company-changes","predictive-problems"]
---

# continuous investigation

Research uses Neyvro objectives, queues, workers, cases, and evidence. Every investigation needs bounded scope, retention, and an explicit stop condition.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when creating, monitoring, reviewing, assigning, or correcting a bounded Neyvro investigation.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.
