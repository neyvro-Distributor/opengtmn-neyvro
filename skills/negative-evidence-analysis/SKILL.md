---
name: negative-evidence-analysis
description: Activate when actively looking for verified facts, missing prerequisites, contradictions, or disqualifiers that weaken an account, buyer, opportunity, or predictive hypothesis.
license: MIT
metadata:
  version: 0.1.0
  maturity: playbook
  mode: research
  required_scopes: ["intelligence:read"]
  related_skills: ["evidence-verification", "buyer-opportunity-matching", "predictive-problem-intelligence"]
---

# Negative evidence analysis

Seek disconfirming evidence rather than only supporting signals. Separate `observed_negative`, `missing_prerequisite`, `contradiction`, `stale_source`, `disqualifier`, and `not_observed`. Return source IDs, freshness, impact, confidence limits, and the condition that would change the conclusion.

Do not treat absence of evidence as proof of absence unless the source coverage and observation window support it. Respect ICP exclusions, opt-outs, tenant boundaries, and customer-approved disqualification rules. Negative findings are read-only and never silently change customer settings.

MCP contracts: `neyvro_get_negative_evidence`, `neyvro_get_evidence`, `neyvro_get_company_signals`, `neyvro_evaluate_icp_fit`.
