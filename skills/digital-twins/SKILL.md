---
name: digital-twins
description: Activate when building or reviewing an evidence-backed, time-aware projection of a company, buyer, or opportunity.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read"]
related_skills: ["account-research","company-changes","evidence","negative-evidence"]
---

# digital twins

Research requires Neyvro company, investigation, and evidence services. A twin is a projection, not ground truth or proof of intent.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when building or reviewing an evidence-backed, time-aware projection of a company, buyer, or opportunity.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.
