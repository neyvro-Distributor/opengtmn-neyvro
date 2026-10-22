---
name: seo-fundamentals
description: Activate when auditing or planning technical, on-page, content, or authority improvements for a website.
version: 0.1.0
maturity: contract
mode: knowledge
required_scopes: []
related_skills: ["generative-engine-optimization","content-marketing-engine"]
---

# seo fundamentals

Explain SEO audits and prioritization. Neyvro currently has no SEO crawler or publisher backend, so live research and external changes are blocked.

## Behavior modes

- Knowledge-only: explain principles and produce no external side effects; no Neyvro login is required.
- Research: call only an authorized Neyvro read contract and return source, freshness, confidence, and unknowns.
- Draft-only: create an editable proposal; do not send, publish, launch, or mutate account state.
- External action: require authenticated workspace scope, provider permission, explicit approval, audit logging, and an idempotency key.

## Contract

- Activation: Activate when auditing or planning technical, on-page, content, or authority improvements for a website.
- Output: structured, reviewable Markdown or JSON with assumptions and evidence references.
- Safety: fail closed when a provider, scope, evidence source, or approval is unavailable.
- Related skills are discovery hints, not implicit context injection.
