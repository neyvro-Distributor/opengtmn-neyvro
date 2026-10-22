---
name: multichannel-sequences
description: Activate when designing, reviewing, compiling, or operating a customer-approved multichannel outreach sequence with deterministic timing, branches, eligibility checks, and stop rules.
license: MIT
metadata:
  version: 0.2.0
  maturity: playbook
  mode: draft
  required_scopes: ["intelligence:read", "proposals:write"]
  related_skills: ["cold-email-writing", "linkedin-outreach", "email-deliverability", "reply-handling-and-objections"]
---

# Multichannel sequences

Design a declarative campaign specification and compile it into a deterministic state machine. Sequence planning and compilation are safe local operations; actual sending must use a separately authorized Neyvro campaign/follow-up backend after explicit customer approval.

## Declarative campaign specification

Each step must define all of these fields:

```json
{
  "step_id": "step-1",
  "channel": "email|linkedin_assisted|authorized_social",
  "recipient": {"buyer_id": "buyer-1", "company_id": "company-1"},
  "sender": {"mailbox_id": "mailbox-1", "identity": "sales@example.com"},
  "message": {"draft_id": "draft-1", "content": "reviewed content"},
  "scheduled_time": "2026-10-24T09:00:00Z",
  "preconditions": ["sender_available", "recipient_eligible", "approval_current"],
  "stop_conditions": ["reply", "unsubscribe", "hard_bounce", "meeting_booked", "customer_cancelled"],
  "approval_version": "approval-v1"
}
```

Only data-defined channels, preconditions, stop conditions, and branch targets are accepted. Never compile or execute arbitrary LLM-generated code. Unsupported channels are rejected or marked `unsupported`; they are never silently treated as email.

## Campaign lifecycle

The compiler and runtime support exactly these states:

`DRAFT → PROPOSED → PENDING_APPROVAL → APPROVED → SCHEDULED → RUNNING → COMPLETED`

Any running campaign may enter `PAUSED`, `CANCELLED`, or `FAILED`. Approval revocation, sender unavailability, recipient ineligibility, provider failure, or an operator pause must prevent dispatch. Approval is versioned; a step approved under an old version cannot run under a new or revoked version.

## Required safety rules

- Stop immediately after a genuine reply, unsubscribe/opt-out, hard bounce, meeting booking, or customer cancellation.
- Recheck sender availability, mailbox permission, recipient eligibility, suppression, current approval version, and channel capability immediately before every dispatch.
- Deduplicate jobs with a deterministic campaign/step/recipient key. Concurrent reply events are idempotent; the first stop event wins and later dispatches are rejected.
- A paused campaign schedules no new work. Resume requires a fresh authorized state transition and eligibility recheck.
- LinkedIn and social steps are assisted unless an officially authorized provider capability exists. Draft/open-profile/manual-action paths must not become automated sends.
- Scheduling must use provider timezone and customer-approved windows; do not assume a local timezone.

## Structured output

Return the declarative spec, compiled state machine, deterministic job IDs, branch/exit rules, approval version, current campaign state, and warnings. Draft/proposal outputs are reviewable and do not send. A send-capable backend must report provider, approval, idempotency, and operation status.

## MCP contracts

- `neyvro_create_campaign_draft` — validate and persist a draft specification.
- `neyvro_propose_campaign` — submit a versioned campaign for customer approval.
- `neyvro_get_campaign` — read the exact campaign specification and version.
- `neyvro_pause_campaign` — request an approved pause/stop through the existing campaign service.
- `neyvro_get_campaign_status` — read state, stop reason, jobs, provider health, and approval version.

Use Neyvro’s existing campaign and follow-up implementation where available. If scheduler integration is absent, return a deterministic schedule plan and `disabled` adapter status; do not create a second sending engine. Sending, scheduling on a live provider, resuming, and cancellation must remain behind the separately authorized approval/idempotency boundary.

See also: `cold-email-writing` for email drafts, `linkedin-outreach` for assisted social steps, `email-deliverability` for sender safety, and `reply-handling-and-objections` for reply-driven stops.
