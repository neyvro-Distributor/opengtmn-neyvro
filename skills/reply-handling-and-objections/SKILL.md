---
name: reply-handling-and-objections
description: Activate when retrieving and classifying an authorized email reply, drafting an objection-aware response, or stopping follow-up after a reply, rejection, unsubscribe, meeting, or out-of-office event.
license: MIT
metadata:
  version: 0.2.0
  maturity: playbook
  mode: research
  required_scopes: ["intelligence:read", "proposals:write"]
  related_skills: ["cold-email-writing", "multichannel-sequences", "discovery-and-qualification"]
---

# Reply handling and objections

Connect Gmail/Microsoft message synchronization and the existing Neyvro follow-up module to a thread-aware reply workflow. The first safe action on any genuine reply is to stop incompatible automatic follow-up before another step can execute. Reading, drafting, and sending are separate permissions; this skill never sends automatically.

## Reply taxonomy

Classify each inbound message into exactly one category:

`INTERESTED`, `REQUEST_INFORMATION`, `NOT_NOW`, `OBJECTION`, `REFERRAL`, `WRONG_PERSON`, `NOT_INTERESTED`, `UNSUBSCRIBE`, `OUT_OF_OFFICE`, `MEETING_REQUEST`, or `UNKNOWN`.

Keep the raw message, thread ID, conversation ID, sender, received time, classifier confidence, evidence/span, and classification version. A duplicate webhook is idempotent. A message from the wrong email thread or tenant is not classified against the campaign.

## Workflow

1. Retrieve the authorized conversation and full thread context. Verify tenant ownership, mailbox provider, sender/recipient identity, thread ID, and campaign/follow-up association.
2. Atomically mark the matching follow-up queue stopped or paused before classification-driven drafting. This guard runs for every genuine reply, including out-of-office and unknown replies.
3. Classify the reply with structured evidence and confidence. Safety-critical `UNSUBSCRIBE` and explicit `NOT_INTERESTED` states immediately suppress future outreach and require no further automated contact.
4. Return a suggested next action: human review, meeting proposal, information draft, referral routing, reminder after a stated out-of-office return date, objection response, or stop/suppress.
5. Draft only after classification and human-review rules permit it. Objection responses acknowledge once, reframe briefly, and ask one next step; do not argue repeatedly. Meeting suggestions use only authorized sender availability and never invent times.
6. Recheck follow-up stop state, suppression, thread, tenant, and approval immediately before any separately authorized send service could act.

## Category actions

- `INTERESTED` / `MEETING_REQUEST`: human review plus a concise meeting suggestion using available times or an approved booking link.
- `REQUEST_INFORMATION`: provide one relevant approved resource, then one soft next-step question.
- `OBJECTION`: acknowledge, address once with approved evidence, and offer one small next step.
- `NOT_NOW`: record the requested timing as a reviewable reminder; do not continue the active cadence.
- `REFERRAL` / `WRONG_PERSON`: thank the sender and request or route to the named responsible person, subject to authorization.
- `NOT_INTERESTED` / `UNSUBSCRIBE`: stop and suppress immediately; no draft is required for unsubscribe.
- `OUT_OF_OFFICE`: stop the active cadence and retain only the provider-return date/alternate that is explicitly present.
- `UNKNOWN`: stop incompatible automation and require human review; never guess intent.

## Structured output

```json
{
  "conversation_id": "conv-1",
  "thread_id": "thread-1",
  "reply_id": "msg-9",
  "category": "INTERESTED",
  "confidence": 0.94,
  "classification_evidence": [{"span": "yes, Thursday works", "source": "msg-9"}],
  "followup_stop": {"required": true, "status": "stopped", "reason": "reply_detected"},
  "suppression": {"required": false, "status": "unchanged"},
  "suggested_next_action": "human_review_meeting_times",
  "draft": null,
  "approval_status": "review_required",
  "send_allowed": false
}
```

## MCP contracts and permissions

- `neyvro_get_conversation` — read tenant-scoped Gmail/Microsoft conversation and thread context.
- `neyvro_get_reply_status` — read classification, stop state, suppression, and processing/idempotency state.
- `neyvro_classify_reply` — classify an authorized inbound reply and apply the stop-on-reply guard.
- `neyvro_draft_reply` — create a human-reviewable objection or meeting response; no send.
- `neyvro_get_followup_queue` — read the current follow-up queue and stopped/paused tasks.

Read contracts require `intelligence:read`; classification/queue stop and draft persistence require the appropriate proposal/follow-up permission; sending belongs to a separate `messages:send` service with explicit approval, mailbox permission, and idempotency key. If Gmail/Microsoft sync or follow-up persistence is unavailable, return `disabled`/`blocked` and do not fabricate a message or stop confirmation.

See also: `cold-email-writing` for copy, `multichannel-sequences` for stop rules, and `discovery-and-qualification` for next-step questions.
