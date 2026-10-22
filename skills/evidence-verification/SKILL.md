---
name: evidence-verification
description: Activate when checking whether a company, buyer, technology, opportunity, or revenue claim is observed, inferred, stale, contradictory, or unsupported by authorized Neyvro evidence.
license: MIT
metadata:
  version: 0.1.0
  maturity: playbook
  mode: research
  required_scopes: ["intelligence:read"]
  related_skills: ["evidence", "negative-evidence-analysis", "company-digital-twin-analysis"]
---

# Evidence verification

Verify claims against tenant-scoped source records and preserve provenance. Distinguish `observed_fact`, `reasonable_inference`, `prediction`, `stale`, `contradictory`, and `unknown`. Report source, observed time, freshness policy, confidence limits, and what would resolve uncertainty.

Inputs include claims, source evidence, freshness threshold, tenant, and optional required source class. Outputs include `verified_claims`, `inferred_claims`, `stale_evidence`, `contradictions`, `unsupported_claims`, `missing_data`, and `verification_status`. Never upgrade an inference into a fact or silently discard negative evidence.

MCP contracts: `neyvro_get_evidence`, `neyvro_get_company_timeline`, `neyvro_get_company_signals`.
