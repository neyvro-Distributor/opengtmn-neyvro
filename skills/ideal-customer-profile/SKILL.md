---
name: ideal-customer-profile
description: Activate when defining, refining, scoring, or reviewing an ideal customer profile, buyer roles, triggers, or anti-ICP.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read"]
related_skills: ["gtm-strategy","account-research","buyer-matching"]
---

# ideal customer profile

Turn onboarding and confirmed research context into explicit, filterable ICP criteria. Research requires authorized Neyvro onboarding/analysis data; writes preserve versioning and workspace ownership.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when defining, refining, scoring, or reviewing an ideal customer profile, buyer roles, triggers, or anti-ICP.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.
