---
name: outbound-metrics-and-benchmarks
description: Activate when analyzing outbound funnel performance, campaign health, attribution, or contextual benchmarks using Neyvro campaign, conversation, and CRM records; every metric must expose its numerator, denominator, time window, segment, and data limitations.
license: MIT
metadata:
  version: 0.2.0
  maturity: playbook
  mode: research
  required_scopes: ["intelligence:read"]
  related_skills: ["cold-email-writing", "email-deliverability", "multichannel-sequences", "linkedin-outreach", "reply-handling-and-objections"]
---

# Outbound metrics and benchmarks

Measure the outbound funnel from sourced contacts through revenue using real, tenant-authorized Neyvro campaign, conversation, mailbox, opportunity, CRM, and cost records. Treat analytics as descriptive unless an experiment or valid causal design supports a stronger conclusion.

## Metric contract

Every returned metric must include:

```json
{
  "metric": "positive_reply_rate",
  "numerator": 0,
  "denominator": 0,
  "rate": null,
  "unit": "ratio",
  "time_window": {"start": "...", "end": "..."},
  "segment": {},
  "sample_size": 0,
  "status": "available|unavailable|insufficient_sample|inconsistent",
  "definition": "unique positive human replies / unique delivered outreach attempts",
  "source_event_ids": [],
  "limitations": []
}
```

Use unique event or entity IDs. Do not count duplicate webhooks twice. A zero denominator yields `rate: null` and `status: unavailable`, never zero. A metric with missing CRM outcomes is unavailable or partial, not a fabricated zero.

Canonical funnel definitions:

- `contacts_found`: unique contacts discovered in the window.
- `contact_verification_rate`: unique contacts with a verified status / unique contacts found.
- `outreach_attempts`: unique authorized send attempts, grouped by campaign and channel.
- `delivery_rate`: unique delivered attempts / unique outreach attempts.
- `bounce_rate`: unique bounced attempts / unique outreach attempts; distinguish hard and soft bounce when available.
- `reply_rate`: unique human replies / unique delivered attempts; exclude automatic replies when classification is available.
- `positive_reply_rate`: unique positive human replies / unique delivered attempts; also report positive share of human replies separately.
- `meetings_booked_rate`: unique meetings booked / unique outreach attempts, plus meetings / positive replies when possible.
- `qualified_opportunity_rate`: unique qualified opportunities / unique outreach attempts; qualification requires CRM evidence, not inference alone.
- `pipeline_value`: sum of authorized opportunity amounts created in the window, with currency and missing-value counts.
- `won_outcomes` and `lost_outcomes`: unique CRM outcomes recorded in the window, with unknown outcomes separated.
- `revenue_attribution`: revenue attached by the customer’s declared attribution model; report model and attribution uncertainty.
- `cost_per_qualified_opportunity`: authorized campaign and provider cost / unique qualified opportunities; unavailable when cost or qualified-opportunity denominator is missing.

## Segmentation and data quality

Allow filters for customer/tenant, ICP segment, industry, signal type, buyer role, campaign, sending channel, sender identity, and time period. Apply tenant filtering before aggregation. Never expose another tenant’s events through a blended benchmark or error message.

Report duplicate IDs, impossible event order, conflicting delivery/reply states, missing CRM opportunity outcomes, unknown currency, stale records, and cross-system mismatches as warnings. A reply without a delivered or sent event is inconsistent unless the provider explicitly supplies the missing history. Preserve raw event provenance and the IDs used in each numerator and denominator.

## Benchmarks and recommendations

External benchmarks are contextual ranges only. They must include source, population, date, denominator, channel, and applicability limitations; never present them as Neyvro targets or guarantees. Do not manufacture a benchmark when no source is supplied.

Use meetings booked, qualified opportunities, pipeline, and revenue as the primary success measures. Reply and positive-reply rates are useful leading indicators. Open rates are directional deliverability diagnostics only and must not be the primary KPI or an A/B winner criterion.

Tie recommendations to observed performance and sample size: identify the lowest trustworthy funnel stage, state whether the sample is sufficient, suggest targeting/copy/list/deliverability/follow-up investigation, and distinguish correlation from causal impact. A segment difference is correlation unless randomized treatment, a credible quasi-experiment, or another causal design is documented.

## MCP contracts

- `neyvro_get_campaign_metrics` — read tenant-authorized campaign, delivery, reply, and meeting events.
- `neyvro_get_pipeline_metrics` — read CRM opportunity stages, amounts, qualification, and outcomes.
- `neyvro_get_revenue_attribution` — read customer-configured attribution and attached revenue.
- `neyvro_get_signal_performance` — compare authorized signal types and segments against downstream outcomes.

These contracts are disabled without real adapters. They must return source freshness, scope, time window, segment, and data-quality warnings. No contract invents CRM outcomes or backend records.

## Required result

Return `metrics`, `definitions`, `segments`, `data_quality`, `benchmarks`, `recommendations`, `causal_limits`, `time_window`, and `tenant_scope`. Include `open_rate_note` stating that opens are not the primary success metric. Never claim revenue attribution, campaign lift, or causal impact when the required records or design are unavailable.

See `multichannel-sequences` for campaign state, `email-deliverability` for sending safety, `reply-handling-and-objections` for reply classification, and `evidence` for provenance.
