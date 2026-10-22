---
name: evidence
description: Activate when collecting, viewing, evaluating, correcting, or citing source-attributed evidence for Neyvro intelligence.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read","proposals:write"]
related_skills: ["account-research","company-changes","negative-evidence","continuous-investigation"]
---

# evidence

Evidence must retain source, observed time, subject, extraction context, and correction history. Missing evidence is not negative evidence unless explicitly classified.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when collecting, viewing, evaluating, correcting, or citing source-attributed evidence for Neyvro intelligence.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.
