---
name: reply-handling-and-objections
description: Activate when classifying a prospect reply, drafting a response, or deciding whether follow-up must stop.
version: 0.1.0
maturity: contract
mode: research
required_scopes: ["intelligence:read","proposals:write"]
related_skills: ["cold-email-writing","discovery-and-qualification","multichannel-sequences"]
---

# reply handling and objections

Research requires authorized mailbox messages. Draft responses are reviewable; sending or changing follow-up state requires approval, mailbox permission, and idempotency.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when classifying a prospect reply, drafting a response, or deciding whether follow-up must stop.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.
