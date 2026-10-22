---
name: outbound-metrics-and-benchmarks
description: Activate when measuring outreach funnels, setting denominators, comparing benchmarks, or diagnosing campaign health.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read"]
related_skills: ["email-deliverability","multichannel-sequences","revenue-attribution"]
---

# outbound metrics and benchmarks

Research may read authorized operations, mailbox, pipeline, and investigation metrics. Report denominators and data gaps; do not claim unsupported attribution.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when measuring outreach funnels, setting denominators, comparing benchmarks, or diagnosing campaign health.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.
