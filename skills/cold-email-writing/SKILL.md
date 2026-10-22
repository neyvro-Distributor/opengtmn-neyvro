---
name: cold-email-writing
description: Activate when drafting or reviewing an evidence-grounded outbound email from an authorized opportunity, buyer, product, positioning, channel, and tone; this skill never sends messages.
license: MIT
metadata:
  version: 0.2.0
  maturity: playbook
  mode: draft
  required_scopes: ["intelligence:read", "proposals:write"]
  related_skills: ["account-research", "outreach-personalization", "email-deliverability", "multichannel-sequences"]
---

# Cold email writing

Create a short, reviewable outbound email with one clear ask. Relevance comes from Neyvro company and buyer evidence; the product message comes only from customer-approved positioning. This skill is draft-only: it must not send, schedule, publish, enroll, or mutate follow-up state.

## Required inputs

Require `opportunity_id`, `buyer_id`, `customer_product`, `approved_positioning`, `channel`, and `tone`. Read the buyer and opportunity through authorized Neyvro services when available. A draft may also receive verified prospect evidence, buyer role/name, company name, framework, and follow-up count. If a required input or evidence source is unavailable, return a flagged draft result rather than inventing it.

## Workflow

1. Confirm the buyer is not suppressed, opted out, an existing customer, or otherwise blocked. A suppressed recipient returns `approval_status: "blocked"` and no sendable body.
2. Select one relevant, recent, verified company signal. Trigger-first personalization is preferred; otherwise use a role/industry observation. Every concrete prospect claim must carry one or more evidence IDs and source metadata.
3. Form a business-relevant problem hypothesis as a question or conditional inference. Never state a business problem, funding event, technology migration, relationship, personal familiarity, result, or testimonial without evidence.
4. Translate only the approved positioning into one buyer-relevant value proposition. Do not add capabilities, metrics, customer names, or outcomes not present in the approved positioning.
5. Use exactly one framework per draft: PAS (problem–agitate–solution), BAB (before–after–bridge), AIDA (attention–interest–desire–action), or trigger-first. Keep the email short and plain-text friendly.
6. End with exactly one low-friction CTA. Follow-up variants are optional drafts and inherit the same evidence and suppression checks.
7. Run `neyvro_check_message_claims` before returning. Any unsupported, unverified, stale, or missing-evidence claim is flagged and prevents `draft_ready` status.

## Output contract

Return a structured result containing:

```json
{
  "opportunity_id": "opp-123",
  "buyer_id": "buyer-456",
  "framework": "trigger-first",
  "subject": "a question about the migration",
  "personalized_opener": {"text": "...", "evidence_ids": ["ev-1"]},
  "problem_hypothesis": {"text": "Could this change be creating ...?", "evidence_ids": ["ev-1"]},
  "value_proposition": {"text": "...", "evidence_ids": ["positioning-v2"]},
  "body": "...",
  "call_to_action": "Worth comparing notes?",
  "follow_up_variants": [],
  "evidence_ids": ["ev-1", "positioning-v2"],
  "flagged_claims": [],
  "approval_status": "draft_ready|needs_evidence|blocked",
  "send_allowed": false
}
```

`send_allowed` is always false. Claim flags must identify the text, reason, and missing or invalid evidence IDs. Approval status means ready for human review, not permission to send.

## Copy rules

- Subject: 1–6 plain words, relevant rather than hype-driven.
- Opener: one sentence about the recipient’s work, not generic praise or private personal details.
- Body: one problem hypothesis, one approved value proposition, and one CTA; avoid feature lists and multiple asks.
- Buyer-specific framing may differ for economic buyers, champions, users, technical evaluators, or approvers, but role assumptions must be marked as assumptions unless verified.
- Keep follow-ups shorter than the initial email and do not introduce a new claim without evidence.

## MCP contracts

- `neyvro_draft_email` — create a draft proposal from authorized opportunity, buyer, evidence, and approved positioning context.
- `neyvro_check_message_claims` — validate prospect and product claims, evidence links, suppression state, and approval readiness.
- `neyvro_get_email_draft` — retrieve an existing draft by exact identifier and version.

These contracts are draft/proposal operations only. Integrate with Neyvro follow-up and outreach services only for supported draft storage or review state; sending requires a separate approved action, mailbox permission, and idempotency key outside this skill.

See also: `account-research` for evidence, `outreach-personalization` for non-creepy relevance, `email-deliverability` for delivery controls, and `multichannel-sequences` for cadence design.
