---
name: company-digital-twin-analysis
description: Activate when reconstructing an authorized company’s current state, historical timeline, transitions, and supporting evidence from Neyvro digital-twin data; never fill unknown fields from assumptions.
license: MIT
metadata:
  version: 0.1.0
  maturity: playbook
  mode: research
  required_scopes: ["intelligence:read"]
  related_skills: ["evidence-verification", "technology-change-detection", "account-research"]
---

# Company digital twin analysis

Read the existing tenant-scoped digital twin, history, transitions, and source records. Return current state, material changes, timeline, evidence references, freshness, contradictions, unknown fields, and research gaps. Do not create a duplicate company database or claim a field that is not present in a verified source.

Inputs: `tenant_id`, `company_id`, authorized twin snapshot, requested freshness, and optional ICP context. Outputs: `current_state`, `historical_timeline`, `transitions`, `supporting_evidence`, `observed_facts`, `inferences`, `unknowns`, `contradictions`, and `status`.

Use verified observations first; label inferences and stale observations separately. Keep customer-approved ICP and access scope unchanged. Knowledge-only explanations remain available without login.

MCP contracts: `neyvro_get_company_twin`, `neyvro_get_company_timeline`, `neyvro_get_company_signals`, `neyvro_get_evidence`.
