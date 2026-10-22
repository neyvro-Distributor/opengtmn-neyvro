---
name: technology-change-detection
description: Activate when identifying authorized, evidence-backed technology adoption, migration, engineering, or infrastructure changes and gaps between current and desired state.
license: MIT
metadata:
  version: 0.1.0
  maturity: playbook
  mode: research
  required_scopes: ["intelligence:read"]
  related_skills: ["company-digital-twin-analysis", "evidence-verification", "predictive-problem-intelligence"]
---

# Technology change detection

Compare observed technology state and timeline transitions with a customer-authorized desired state. Classify changes as adoption, migration, deprecation, engineering hiring or investment, security requirement, cloud expansion, or unknown. Every change must carry source IDs, observation time, freshness, and confidence.

Return `changes`, `technology_gaps`, `observed_facts`, `inferences`, `unknowns`, `contradictions`, and `research_gaps`. A detected signal is not proof of a project, budget, pain, or buying intent. Do not infer technology from a job title alone, and do not crawl or alter systems without authorization.

MCP contracts: `neyvro_get_company_twin`, `neyvro_get_company_signals`, `neyvro_get_company_timeline`, `neyvro_get_evidence`.
