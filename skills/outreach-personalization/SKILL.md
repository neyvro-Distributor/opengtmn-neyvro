---
name: outreach-personalization
description: Activate when turning authorized company, buyer, opportunity, positioning, and brand-voice context into evidence-linked personalization snippets at strategic, qualified, or lightweight effort levels; never send messages.
license: MIT
metadata:
  version: 0.2.0
  maturity: playbook
  mode: draft
  required_scopes: ["intelligence:read", "proposals:write"]
  related_skills: ["account-research", "cold-email-writing", "linkedin-outreach", "ideal-customer-profile"]
---

# Outreach personalization

Create reusable, channel-neutral snippets that make outreach relevant without pretending familiarity. Use customer-approved positioning, digital-twin state, verified company signals, buyer responsibilities, opportunity hypotheses, authorized relationship history, and approved brand voice. This skill drafts and validates only; it never sends messages.

## Effort levels

| Level | Use when | Required personalization |
| --- | --- | --- |
| High-touch strategic | A-tier or strategic opportunity | verified trigger, why-now context, buyer responsibility, pain hypothesis, approved benefit, proof, and one CTA |
| Medium-touch qualified | ICP-fit account with bounded research | one verified company signal, role-relevant hypothesis, approved benefit, and one CTA |
| Lightweight relevant | volume or low-information account | generic product messaging plus verified role/industry framing; no invented account claim |

Effort controls research and copy depth; it never lowers evidence or authorization standards. If evidence is insufficient for the selected level, downgrade the output or return `needs_evidence`.

## Snippet categories

Return swappable snippets for:

- `verified_trigger` — one current, source-linked company change;
- `why_now` — why the change may make the conversation timely, clearly labeled as an inference;
- `relevant_pain_hypothesis` — a conditional, buyer-role-specific hypothesis, never a stated fact without evidence;
- `product_benefit` — approved positioning or clearly labeled generic product messaging;
- `proof_point` — approved, source-linked proof only;
- `call_to_action` — one low-friction ask, without a guarantee.

Every non-generic snippet carries `evidence_ids`, source references, observed time, and confidence. Generic product messaging is labeled `generic: true` and must not be presented as prospect personalization.

## Workflow and guardrails

1. Read the authorized customer positioning, brand voice, company twin/signals, buyer responsibilities, opportunity hypothesis, and relationship history. Keep tenant and recipient scope intact.
2. Select at most one strongest current trigger. Contradictory signals remain visible, lower confidence, and block a trigger claim until resolved.
3. Match the angle to the buyer’s verified role and responsibilities. If the evidence concerns another role, mark `buyer_role_mismatch` and do not use it as individualized copy.
4. Separate observation, inference, generic product material, and proof. Never fabricate familiarity, compliments, personal details, outcomes, customer results, guarantees, or product capabilities.
5. Avoid identical bodies across recipients. A reusable category is acceptable; the individualized trigger or role framing must differ when the account has distinct evidence. If no evidence differs, return generic messaging instead of fake personalization.
6. Validate all snippets with `neyvro_validate_outreach_claims`. The result is reviewable draft material, never a send authorization.

## Structured output

```json
{
  "effort_level": "high_touch_strategic|medium_touch_qualified|lightweight_relevant",
  "snippets": [{"category": "verified_trigger", "text": "...", "evidence_ids": ["ev-1"], "generic": false, "confidence": 0.9}],
  "confidence_limitations": [],
  "evidence_links": [{"evidence_id": "ev-1", "source": "...", "observed_at": "..."}],
  "flagged_claims": [],
  "brand_voice": {"status": "consistent|unknown|flagged", "applied": "..."},
  "approval_status": "draft_ready|needs_evidence|blocked",
  "send_allowed": false
}
```

## MCP contracts

- `neyvro_get_personalization_context` — read tenant-scoped positioning, digital-twin signals, buyer responsibilities, opportunity hypothesis, authorized relationship history, and brand voice.
- `neyvro_generate_personalization` — generate versioned reviewable snippets for a selected effort level.
- `neyvro_validate_outreach_claims` — validate evidence links, role fit, contradictions, generic labels, and brand-voice constraints.
- `neyvro_get_brand_voice` — read the customer-approved voice and version.

These contracts require an authorized adapter and never send. Integrate with cold email, LinkedIn-assisted, or sequence workflows only by passing reviewable draft snippets; external action remains separately approval-gated.

See also: `account-research` for signals, `cold-email-writing` for email composition, `linkedin-outreach` for assisted social use, and `ideal-customer-profile` for buyer fit.
