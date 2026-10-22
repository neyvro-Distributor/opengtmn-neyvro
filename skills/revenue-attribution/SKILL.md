---
name: revenue-attribution
description: Activate when tracing authorized signals through buyers, campaigns, meetings, opportunities, deals, and revenue using an explicit attribution model and complete provenance.
license: MIT
metadata:
  version: 0.2.0
  maturity: playbook
  mode: research
  required_scopes: ["intelligence:read"]
  related_skills: ["outbound-metrics-and-benchmarks", "evidence-verification", "continuous-account-investigation"]
---

# Revenue attribution

Trace signal, buyer, campaign, message, meeting, opportunity, deal, and revenue events only when authorized records can be joined. Return `touchpoints`, `opportunity_links`, `attributed_revenue`, `model`, `unattributed_events`, `missing_links`, `data_quality`, and `causal_limits`.

Always state whether the result is first-touch, last-touch, multi-touch, account-level influence, or another customer-declared model. Distinguish correlation, influence, and verified attribution. Do not claim causation, revenue, or campaign lift when CRM outcomes, timestamps, currency, identity joins, or model configuration are missing. Never mutate CRM records.

MCP contracts: `neyvro_get_revenue_attribution`, `neyvro_get_pipeline_metrics`, `neyvro_get_campaign_metrics`, `neyvro_get_evidence`.
