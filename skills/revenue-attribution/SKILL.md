---
name: revenue-attribution
description: Activate when linking evidence and approved GTM actions to pipeline or revenue outcomes with explicit attribution limits.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read"]
related_skills: ["outbound-metrics-and-benchmarks","continuous-investigation","evidence"]
---

# revenue attribution

Distinguish correlation, influence, and verified revenue attribution. Do not mutate CRM or claim causal revenue impact without a defined model and complete event data.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when linking evidence and approved GTM actions to pipeline or revenue outcomes with explicit attribution limits.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.
