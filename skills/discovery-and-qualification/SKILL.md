---
name: discovery-and-qualification
description: Activate when evaluating whether a company or contact is a qualified opportunity and preparing discovery questions.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read"]
related_skills: ["ideal-customer-profile","buyer-matching","predictive-problems"]
---

# discovery and qualification

Research may read authorized company, buyer, investigation, and pipeline context. Unknown is a valid result and must not become a positive score.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when evaluating whether a company or contact is a qualified opportunity and preparing discovery questions.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.
