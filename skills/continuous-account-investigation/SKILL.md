---
name: continuous-account-investigation
description: Activate when reviewing unresolved company questions, selecting permitted next research actions, and enforcing freshness, scope, cost, and research-budget limits for ongoing account investigation.
license: MIT
metadata:
  version: 0.1.0
  maturity: playbook
  mode: research
  required_scopes: ["intelligence:read"]
  related_skills: ["company-digital-twin-analysis", "evidence-verification", "negative-evidence-analysis"]
---

# Continuous account investigation

Retrieve the existing investigation state and unresolved questions before proposing research. Rank permitted next actions by expected information value, evidence freshness, customer ICP relevance, cost, rate limit, and authorization. Return `unresolved_questions`, `allowed_actions`, `blocked_actions`, `budget_remaining`, `stopping_conditions`, and `status`.

Do not repeatedly crawl fresh sources, run paid research without entitlement, or trigger jobs without an authorized budget and audit record. A research plan is not a completed investigation and must not fabricate findings.

MCP contracts: `neyvro_get_investigation_status`, `neyvro_get_company_timeline`, `neyvro_get_evidence`, `neyvro_research_company`.
