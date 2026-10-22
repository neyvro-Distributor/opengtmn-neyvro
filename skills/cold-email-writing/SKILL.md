---
name: cold-email-writing
description: Activate when drafting or reviewing a personalized cold email or short sequence from authorized evidence.
version: 0.1.0
maturity: contract
mode: draft
required_scopes: ["intelligence:read","proposals:write"]
related_skills: ["account-research","outreach-personalization","email-deliverability"]
---

# cold email writing

Draft mode creates editable, evidence-linked variants with one clear ask. Sending or scheduling is external action requiring an approved proposal, mailbox permission, and idempotency key.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when drafting or reviewing a personalized cold email or short sequence from authorized evidence.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.
