---
name: positioning-and-messaging
description: Activate when translating a product's differentiated value into positioning, message houses, or evidence-backed outreach angles.
version: 0.1.0
maturity: contract
mode: draft
required_scopes: ["intelligence:read"]
related_skills: ["gtm-strategy","ideal-customer-profile","cold-email-writing"]
---

# positioning and messaging

Use supplied or authorized brief evidence to draft positioning and messaging. Draft mode produces editable artifacts; external publishing or sending requires approval.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when translating a product's differentiated value into positioning, message houses, or evidence-backed outreach angles.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.
