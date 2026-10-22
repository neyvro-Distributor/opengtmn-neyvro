---
name: lead-sourcing-and-enrichment
description: Activate when finding or enriching ICP-fit companies and contacts with verified, source-labeled data.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read"]
related_skills: ["ideal-customer-profile","account-research","evidence"]
---

# lead sourcing and enrichment

Research requires authorized Neyvro providers and must preserve source, verification, freshness, and suppression states. Never guess an identity or email.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when finding or enriching ICP-fit companies and contacts with verified, source-labeled data.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.
