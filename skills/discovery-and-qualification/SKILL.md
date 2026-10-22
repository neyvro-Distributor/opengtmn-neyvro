---
name: discovery-and-qualification
description: Activate when qualifying an authorized sales opportunity or preparing a discovery-call brief using evidence, buyer research, conversation context, CRM records, and meeting history; never qualify from AI inference alone.
license: MIT
metadata:
  version: 0.2.0
  maturity: playbook
  mode: research
  required_scopes: ["intelligence:read"]
  related_skills: ["ideal-customer-profile", "buyer-matching", "predictive-problems", "reply-handling-and-objections"]
---

# Discovery and qualification

Prepare an evidence-backed account briefing and discovery plan. Use BANT for a fast first pass, MEDDIC for complex opportunities, and MEDDPICC when paper process and competition materially affect the deal. Framework fields are lenses for questions, not permission to infer budget, authority, need, timing, or purchase intent.

## Qualification workflow

1. Retrieve the opportunity, authorized company/buyer context, conversation thread, meeting history, existing CRM record, and opportunity evidence. Preserve tenant scope and source timestamps.
2. Separate `confirmed_facts`, `inferences`, `qualification_gaps`, and `conflicting_information`. Only verified, attributable evidence can populate confirmed facts.
3. Map the buying committee: economic buyer, champion, users, technical evaluator, procurement/legal, approver, and blockers. A title or AI guess is a stakeholder hypothesis until verified.
4. Assess pain severity and cost of inaction from the buyer’s own words or evidence. Treat an inferred pain as a discovery question, not a qualification fact.
5. Assess budget, timing, decision criteria/process, competition, and paper process only when explicitly supported. Never invent a budget, purchase timeline, authority, or commitment.
6. Apply disqualification rules: explicit no need, out-of-scope/anti-ICP, no permitted buyer path, suppression/opt-out, duplicate or wrong opportunity, or a customer-confirmed blocker. Record the evidence and do not override it with a predicted score.
7. Produce the brief, recommended questions, relevant objections, and one suggested next step. If CRM or meeting APIs are absent, keep the brief read-only and list the exact missing context.

## Framework lenses

- **BANT:** Budget, Authority, Need, Timeline. Unknown budget or timing stays unknown.
- **MEDDIC:** Metrics, Economic buyer, Decision criteria, Decision process, Identify pain, Champion.
- **MEDDPICC:** MEDDIC plus Paper process and Competition.

Select one primary framework and show the evidence status for every dimension. Do not aggregate unknowns into a positive score. A deal can be `qualified` only when the required dimensions for the selected framework are explicitly evidenced, the buyer path is credible, and no disqualifier or unresolved contradiction remains.

## Required output

```json
{
  "opportunity_id": "opp-123",
  "framework": "BANT|MEDDIC|MEDDPICC",
  "status": "qualified|incomplete|needs_review|nonbuyer|disqualified",
  "account_briefing": "...",
  "confirmed_facts": [],
  "qualification_dimensions": {"budget": {"status": "confirmed|unknown|conflicting", "evidence_ids": []}},
  "qualification_gaps": [],
  "conflicting_information": [],
  "buying_committee": [],
  "pain_severity": {"status": "confirmed|hypothesis|unknown", "evidence_ids": []},
  "relevant_objections": [],
  "recommended_discovery_questions": [],
  "suggested_next_step": "...",
  "research_gaps": [],
  "approval_status": "read_only|review_required",
  "send_allowed": false
}
```

`confirmed_facts` and each dimension’s evidence IDs must be source-attributed. A qualification status is not a forecast, win probability, or authorization to send. Discovery questions should resolve the highest-value gap first and must not presuppose a problem, budget, or timeline.

## MCP contracts

- `neyvro_get_opportunity_qualification` — read the current opportunity, qualification fields, evidence, CRM stage, and disqualifiers.
- `neyvro_generate_discovery_brief` — generate a versioned, read-only account briefing and question plan.
- `neyvro_get_buying_committee` — read authorized stakeholders, responsibilities, influence, and evidence.
- `neyvro_get_meeting_context` — read synchronized meeting notes, transcript summaries, and prior commitments when available.

These are read/planning contracts. If CRM or meeting APIs are missing, return `disabled`/`unknown` fields and preserve knowledge-only discovery guidance. No contract changes CRM qualification or sends a message.

See also: `ideal-customer-profile` for fit and disqualification, `buyer-matching` for roles, `account-research` for company evidence, and `reply-handling-and-objections` for conversation context.
