---
name: multichannel-sequences
description: Activate when designing, reviewing, or operating a multi-step outreach cadence with explicit branch and stop logic.
version: 0.1.0
maturity: contract
mode: draft
required_scopes: ["proposals:write"]
related_skills: ["cold-email-writing","linkedin-outreach","reply-handling-and-objections"]
---

# multichannel sequences

Draft mode produces steps, timing, branches, suppression rules, and a proposed sequence. Launch, pause, resume, or send requires approval, provider permissions, and idempotent operations.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when designing, reviewing, or operating a multi-step outreach cadence with explicit branch and stop logic.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.
