---
name: buyer-matching
description: Activate when matching a target account or problem to buyer roles using authorized company and contact evidence.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read"]
related_skills: ["ideal-customer-profile","lead-sourcing-and-enrichment","discovery-and-qualification"]
---

# buyer matching

Separate role fit from verified identity and contactability. No person or email may be invented.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when matching a target account or problem to buyer roles using authorized company and contact evidence.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.
