---
name: linkedin-outreach
description: Activate when researching an authorized professional profile, selecting a relevant LinkedIn outreach angle, drafting a connection note or direct message, or recording customer-confirmed manual outreach; never automate LinkedIn actions.
license: MIT
metadata:
  version: 0.2.0
  maturity: playbook
  mode: draft
  required_scopes: ["intelligence:read", "proposals:write"]
  related_skills: ["account-research", "outreach-personalization", "multichannel-sequences", "cold-email-writing"]
---

# LinkedIn outreach

Assist compliant professional relationship outreach using verified company and buyer evidence. LinkedIn is an assisted channel in Neyvro: research permitted context, draft, review, open the profile, let the customer act manually, and record the customer-confirmed action.

## Supported workflow

1. Read an authorized prospect profile, company context, current role, relationship state, and dated professional evidence. Cross-tenant IDs are non-disclosing `not_found`/`forbidden` results.
2. Check profile freshness and current-role evidence. If the profile is missing, stale, unauthorized, or provider-restricted, report the gap rather than guessing.
3. Select one work-relevant angle: a verified company change, a verified professional post or stated responsibility, or an authorized relationship context. Avoid sensitive personal traits, private details, generic praise, and manufactured familiarity.
4. Draft one of: a pitch-free connection note, a short direct message for an existing relationship, or a meaningful engagement suggestion tied to a verified post. Keep each claim linked to evidence IDs.
5. Require customer review and approval. The customer opens the profile and manually performs the action on LinkedIn. Record only a customer-confirmed action and its timestamp.
6. For relationship-aware follow-up, read the recorded relationship state and stop when the prospect declined, opted out, or no longer has a verified current role. Never infer acceptance, reply, or relationship status from an attempted draft.

## Explicitly unsupported

Neyvro must not build or use unauthorized scraping, browser-account hijacking, cookie-based bots, stealth automation, prohibited bulk connection requests, automated DMs, automated comments/reactions, or any capability that violates LinkedIn or provider terms. Direct send/connection/comment tools are unsupported unless an officially authorized platform capability is later supplied and separately approved. Never fabricate execution, delivery, acceptance, or engagement.

## Draft outputs

Return structured drafts such as:

```json
{
  "status": "draft_ready|needs_evidence|stale|missing_profile|unsupported|blocked",
  "prospect_id": "person-123",
  "action": "connection_note|direct_message|engagement_suggestion",
  "message": "...",
  "engagement_suggestion": null,
  "angle": "...",
  "evidence_ids": ["ev-1"],
  "flagged_claims": [],
  "relationship_state": "not_connected|pending|connected|unknown",
  "approval_status": "review_required|blocked|unsupported",
  "manual_steps": ["Review draft", "Open profile", "Customer acts manually", "Record confirmed action"],
  "external_action_executed": false
}
```

Connection notes should be brief and non-pitchy. A direct message should be drafted only when relationship context permits it; otherwise return a connection-note suggestion. Engagement should add a real professional observation, not a disguised sales pitch. One soft ask maximum, and no automated follow-up.

## MCP contracts

- `neyvro_get_linkedin_prospect_context` — read tenant-scoped professional profile, company, role, permitted posts, evidence, and freshness.
- `neyvro_draft_linkedin_message` — create a reviewable connection-note, DM, or engagement draft; it does not send or publish.
- `neyvro_get_social_relationship` — read authorized connection, prior interaction, opt-out, and follow-up state.
- `neyvro_record_manual_outreach` — record an action only after the customer confirms they manually performed it; it does not call LinkedIn.

All contracts require an authorized adapter and tenant scope. If a provider is unavailable, return `disabled` with setup requirements. Provider setup must use officially authorized platform capabilities and permitted data providers; credentials, cookies, and session tokens never belong in skills or logs.

See also: `account-research` for company evidence, `outreach-personalization` for relevance, `multichannel-sequences` for reviewable cadence, and `cold-email-writing` for email alternatives.
