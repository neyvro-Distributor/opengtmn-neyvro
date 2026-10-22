---
name: email-deliverability
description: Activate when assessing authorized Gmail or Microsoft mailbox readiness, SPF/DKIM/DMARC configuration, sender limits, bounce or complaint risk, recipient hygiene, or safe email ramp-up; never change DNS or send mail.
license: MIT
metadata:
  version: 0.2.0
  maturity: playbook
  mode: research
  required_scopes: ["intelligence:read"]
  related_skills: ["cold-email-writing", "multichannel-sequences", "outbound-metrics-and-benchmarks"]
---

# Email deliverability

Assess sender safety from authorized mailbox/provider telemetry and explicitly reported DNS configuration. Deliverability is an operational health review, not a promise of inbox placement. Never invent scores, provider health, DNS records, or metrics.

## Operating modes

- **Knowledge-only:** explain SPF, DKIM, DMARC, pacing, list hygiene, bounce, complaint, and unsubscribe controls without login or external calls.
- **Connected read-only audit:** inspect authorized Gmail or Microsoft mailbox connection status, provider-reported limits/metrics, recipient verification, suppression, and any customer-authorized DNS evidence.
- **Draft-only remediation:** produce an editable checklist or ramp recommendation. Do not change DNS, mailbox settings, sender identity, limits, or sending volume.
- **External action:** test mail, DNS updates, mailbox changes, and sends require the relevant provider permission and explicit approval; this skill exposes no mutation or send operation.

## Audit sequence

1. Confirm the mailbox provider (`gmail` or `microsoft`), authorized connection, sender identity, sending domain, and tenant/workspace scope. A disconnected or unauthorized mailbox is `blocked` for sending readiness.
2. Check SPF, DKIM, and DMARC only from an authorized DNS check or customer-supplied record. If DNS access was not authorized, report `unknown`—do not perform a lookup or infer a pass.
3. Read provider-reported daily limits, sent count, remaining capacity, throttles, bounces, complaints, and unsubscribe events. Include the provider, observation time, and measurement window.
4. Check recipient hygiene before any proposed send: verified status, stale/unverified addresses, catch-all/risky addresses, opt-outs, suppression lists, repeated bounces, existing customers, and active follow-up stops.
5. Compare observed volume with the configured limit and ramp stage. Recommend gradual ramp-up and even pacing for new senders; warmup is guidance, never a guarantee of deliverability.
6. Return verified checks, provider health signals, best-practice recommendations, and unknown/unavailable metrics as separate sections. Use the most restrictive safe interpretation when a hard safety signal is present.

## Authentication guidance

| Check | Safe interpretation |
| --- | --- |
| SPF | One authoritative SPF record should authorize all actual sending services; missing, conflicting, or unverified is not ready. |
| DKIM | Signing should be enabled for the sending domain/provider; an unknown selector or unverified signature remains unknown. |
| DMARC | A published policy and aligned SPF/DKIM are required for a trustworthy configuration; report the observed policy without promising placement. |
| Sender identity | The authenticated mailbox and From identity must be authorized by the provider and workspace. |

Do not require direct DNS access when the customer has not authorized it. Never change DNS automatically. Do not send an external test message without approval.

## Safety thresholds and recommendations

Treat provider thresholds as authoritative when supplied; otherwise label benchmark guidance as a recommendation, not an observed result. Stop or review when daily limits are exceeded, repeated bounces rise, complaints occur, recipients are unverified, or suppression/opt-out state is uncertain. Honor unsubscribe and suppression immediately. Do not claim an inbox-placement percentage from bounce, open, or reply data.

## Required output

Return structured data with:

```json
{
  "status": "ready|review|blocked|unknown",
  "provider": "gmail|microsoft|unknown",
  "verified_configuration_checks": [],
  "provider_health_signals": [],
  "recommendations": [],
  "unknown_metrics": [],
  "recipient_safety": {"unverified": 0, "suppressed": 0, "repeated_bounces": 0},
  "sender_limits": {"daily_limit": null, "sent_today": null, "remaining": null},
  "authentication": {"spf": "verified|missing|failed|unknown", "dkim": "verified|missing|failed|unknown", "dmarc": "verified|missing|failed|unknown"},
  "send_allowed": false
}
```

Every observed check includes source, observed time, and provider where available. `send_allowed` is always false: this skill can inform another approved workflow but cannot send, warm up, schedule, or mutate configuration.

## Optional read-only MCP contracts

- `neyvro_get_mailbox_health` — Gmail/Microsoft connection, sender identity, authorization, and provider health.
- `neyvro_get_sender_limits` — provider limits, sent count, remaining capacity, throttles, and ramp state.
- `neyvro_get_delivery_metrics` — provider-reported bounce, complaint, unsubscribe, and delivery metrics with windows.
- `neyvro_audit_email_configuration` — authorized SPF/DKIM/DMARC and sender-configuration audit.

They are disabled without an authenticated adapter. Adapter setup requires a tenant-scoped Gmail or Microsoft connection, read-only provider permission, provider credential reference, and—only if DNS checks are requested—explicit customer authorization for DNS inspection. No credentials belong in skill files.

See also: `cold-email-writing` for copy, `multichannel-sequences` for cadence, and `outbound-metrics-and-benchmarks` for denominators and trend analysis.
