---
name: negative-evidence
description: Activate when recording, evaluating, or explaining disconfirming evidence, missing signals, or reasons not to act.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read","proposals:write"]
related_skills: ["evidence","predictive-problems","continuous-investigation"]
---

# negative evidence

Separate absence, unknown, and contradiction. Never claim “not found” means “does not exist.”

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when recording, evaluating, or explaining disconfirming evidence, missing signals, or reasons not to act.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.
