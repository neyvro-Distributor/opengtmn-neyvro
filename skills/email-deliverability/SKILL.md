---
name: email-deliverability
description: Activate when assessing sending-domain readiness, authentication, reputation, pacing, bounce, or complaint risk.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read"]
related_skills: ["cold-email-writing","multichannel-sequences","outbound-metrics-and-benchmarks"]
---

# email deliverability

Research may inspect authorized mailbox and operation status. Draft mode produces remediation plans; it must not change DNS, mailbox settings, or send volume.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when assessing sending-domain readiness, authentication, reputation, pacing, bounce, or complaint risk.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.
