---
name: buyer-opportunity-matching
description: Activate when matching an evidence-backed company problem or opportunity to people likely responsible for solving, influencing, approving, or blocking it.
license: MIT
metadata:
  version: 0.1.0
  maturity: playbook
  mode: research
  required_scopes: ["intelligence:read"]
  related_skills: ["lead-sourcing-and-enrichment", "discovery-and-qualification", "evidence-verification"]
---

# Buyer opportunity matching

Match a verified problem to buyer responsibilities and a buying committee using authorized buyer, opportunity, CRM, and evidence records. Return `matches` with role, responsibility, evidence IDs, freshness, confidence limits, and missing stakeholders. Keep decision-maker, champion, economic buyer, and influencer labels distinct.

Do not guess identity, contact details, authority, or intent. Existing customers, opt-outs, suppressed contacts, and cross-tenant records remain excluded. A matched role is not a qualified opportunity. Contact enrichment and outreach remain separate permissioned workflows.

MCP contracts: `neyvro_search_buyers`, `neyvro_get_opportunity_buyers`, `neyvro_get_buying_committee`, `neyvro_get_evidence`.
