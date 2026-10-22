---
name: predictive-problem-intelligence
description: Activate when mapping verified company or technology changes to possible customer-relevant problems, while keeping hypotheses distinct from facts and respecting the customer ICP.
license: MIT
metadata:
  version: 0.1.0
  maturity: playbook
  mode: research
  required_scopes: ["intelligence:read"]
  related_skills: ["technology-change-detection", "ideal-customer-profile", "evidence-verification"]
---

# Predictive problem intelligence

Use verified changes, approved ICP criteria, product context, and historical evidence to propose possible problems worth validating. Return each hypothesis with triggering evidence, ICP relevance, alternative explanations, uncertainty, and a validation question. Never state a predicted problem as a confirmed customer need or fabricate predictive confidence.

Outputs: `problem_hypotheses`, `supporting_evidence`, `counter_evidence`, `validation_questions`, `unknowns`, `disqualifiers`, and `status`. A single weak signal cannot qualify an account. Read-only MCP access is preferred; controlled research jobs require authorization, cost budget, and audit logging.

MCP contracts: `neyvro_get_company_signals`, `neyvro_get_predictive_opportunities`, `neyvro_evaluate_icp_fit`, `neyvro_get_evidence`.
