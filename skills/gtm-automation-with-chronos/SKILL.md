---
name: gtm-automation-with-chronos
description: Activate when a user asks to turn GTM planning into external execution through an authorized MCP or provider.
version: 0.1.0
maturity: contract
mode: execution
required_scopes: ["proposals:write","messages:send"]
related_skills: ["multichannel-sequences","cold-email-writing","lead-sourcing-and-enrichment"]
---

# gtm automation with chronos

Use Neyvro's capability registry and approval flow; OpenGTM's documented Chronos geo_* tools are not local Neyvro tools. Refuse execution when scope, provider, or approval is missing.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when a user asks to turn GTM planning into external execution through an authorized MCP or provider.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.
