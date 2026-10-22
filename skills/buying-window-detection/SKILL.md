---
name: buying-window-detection
description: Activate when assessing whether verified company, leadership, technology, funding, security, hiring, or product signals justify attention now under the customer’s ICP and authorization rules.
license: MIT
metadata:
  version: 0.1.0
  maturity: playbook
  mode: research
  required_scopes: ["intelligence:read"]
  related_skills: ["predictive-problem-intelligence", "technology-change-detection", "evidence-verification"]
---

# Buying-window detection

Explain why an opportunity may deserve attention now using fresh, relevant, multi-source evidence. Return `window_reasons`, `timing_evidence`, `counter_evidence`, `recommended_expiry`, `validation_questions`, `uncertainty`, and `status`. Do not invent budget, project dates, urgency, or intent; a signal is not a buying window by itself.

Respect customer ICP, suppression, relationship, and research-budget settings. If evidence is stale, contradictory, or incomplete, downgrade the result and state what is unknown. Read-only analysis is the default; job triggers need authorization, cost budgets, and audit logs.

MCP contracts: `neyvro_get_buying_windows`, `neyvro_get_company_signals`, `neyvro_get_company_timeline`, `neyvro_get_evidence`.
