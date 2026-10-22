---
name: gtm-automation-with-neyvro
description: Activate when coordinating Neyvro knowledge skills with connected customer intelligence, research, drafting, campaign, mailbox, conversation, meeting, SEO/GEO, content, or analytics services; use capability discovery and approval gates before any external action.
license: MIT
metadata:
  version: 0.2.0
  maturity: playbook
  mode: execution
  required_scopes: ["intelligence:read"]
  related_skills: ["gtm-strategy", "multichannel-sequences", "outbound-metrics-and-benchmarks", "evidence"]
---

# GTM automation with Neyvro

This is Neyvro’s native bridge between portable knowledge skills and authorized Neyvro MCP services. It does not require Chronos accounts, Chronos APIs, or `geo_*` tools. A Markdown skill remains useful without an account; this bridge discovers whether Neyvro can supply live context or execute an explicitly approved operation.

## Capability discovery

Before using connected data or proposing execution, call the capability contracts and determine:

- whether Neyvro is connected and authentication is valid;
- which scopes are granted and which are required;
- which services are implemented, unavailable, disabled, or blocked;
- which Gmail, Microsoft, social, website, repository, CRM, or other accounts are connected;
- which actions require customer approval and whether the exact approval is current;
- the tenant, freshness, provider, rate-limit, and data-quality boundaries.

Do not infer a connected account from a configured name, a skill description, or a documented tool. A service is available only when the server reports it available for the current tenant and scopes.

## Skill-to-capability map

Use metadata discovery first and load one exact skill on demand. The bridge map is maintained in `src/neyvro/gtm_automation.py`; it does not inject all skill documents into an agent request.

| Capability group | Portable skills | Neyvro-native tools |
|---|---|---|
| Customer strategy and ICP | `gtm-strategy`, `ideal-customer-profile`, `positioning-and-messaging` | `neyvro_get_customer_context`, `neyvro_get_gtm_strategy`, `neyvro_get_icp`, `neyvro_evaluate_icp_fit`, `neyvro_get_product_context`, `neyvro_get_positioning`, `neyvro_get_approved_claims` |
| Company research | `account-research`, `digital-twins`, `company-changes` | `neyvro_research_company`, `neyvro_get_company_twin`, `neyvro_get_company_signals`, `neyvro_get_company_timeline` |
| Monitoring and evidence | `evidence`, `negative-evidence`, `continuous-investigation` | `neyvro_get_evidence`, `neyvro_get_company_signals`, `neyvro_get_company_timeline`, `neyvro_get_investigation_status` |
| Predictive opportunities | `predictive-problems`, `buying-windows` | `neyvro_get_predictive_opportunities`, `neyvro_get_buying_windows`, `neyvro_get_opportunity_signals` |
| Buyer discovery | `buyer-matching`, `lead-sourcing-and-enrichment`, `discovery-and-qualification` | `neyvro_search_buyers`, `neyvro_get_opportunity_buyers`, `neyvro_get_opportunity_qualification`, `neyvro_get_buying_committee` |
| Contact enrichment | `lead-sourcing-and-enrichment` | `neyvro_enrich_contact`, `neyvro_get_contact_verification` |
| Message personalization | `outreach-personalization`, `linkedin-outreach` | `neyvro_get_personalization_context`, `neyvro_generate_personalization`, `neyvro_get_brand_voice`, `neyvro_get_linkedin_prospect_context` |
| Email drafting | `cold-email-writing`, `email-deliverability` | `neyvro_draft_email`, `neyvro_check_message_claims`, `neyvro_get_mailbox_health`, `neyvro_get_sender_limits` |
| Campaign proposals | `multichannel-sequences`, `content-marketing-engine` | `neyvro_create_campaign_draft`, `neyvro_propose_campaign`, `neyvro_create_content_brief`, `neyvro_propose_social_post` |
| Approved campaign execution | `multichannel-sequences`, `email-deliverability` | `neyvro_execute_approved_campaign`, `neyvro_get_campaign_status`, `neyvro_get_delivery_metrics` |
| Conversation intelligence | `reply-handling-and-objections` | `neyvro_get_conversation`, `neyvro_get_reply_status`, `neyvro_classify_reply`, `neyvro_get_followup_queue` |
| Meeting and pipeline intelligence | `discovery-and-qualification`, `revenue-attribution` | `neyvro_get_meeting_context`, `neyvro_get_opportunity_qualification`, `neyvro_get_pipeline_metrics`, `neyvro_get_revenue_attribution` |
| SEO/GEO analysis | `seo-fundamentals`, `generative-engine-optimization` | `neyvro_analyze_website`, `neyvro_get_seo_recommendations`, `neyvro_get_geo_audit`, `neyvro_get_ai_visibility_findings` |
| Content workflows | `content-marketing-engine` | `neyvro_generate_content_ideas`, `neyvro_create_content_brief`, `neyvro_draft_content`, `neyvro_get_content_calendar` |
| Analytics and revenue learning | `outbound-metrics-and-benchmarks`, `revenue-attribution` | `neyvro_get_campaign_metrics`, `neyvro_get_pipeline_metrics`, `neyvro_get_revenue_attribution`, `neyvro_get_signal_performance` |

The map is a routing contract, not proof that every service is currently implemented. The capability response must mark unavailable tools explicitly.

## Operating pattern

Coordinate work through:

`RESEARCH -> PLAN -> DRAFT -> REVIEW -> APPROVE -> EXECUTE -> VERIFY -> LEARN`

Knowledge-only work may stop after PLAN or DRAFT and remains useful while disconnected. Connected reads require valid authentication, tenant scope, and `intelligence:read`. Drafts and proposals never send, publish, schedule, change DNS, merge, deploy, or alter CRM state.

External execution requires all of the following at the server boundary:

1. a connected account and implemented service;
2. valid authentication and required scopes;
3. exact current approval for the action, content, recipients, channel, timing, and approval version;
4. eligibility, suppression, deliverability, and idempotency checks;
5. an audit record and post-action verification.

If any gate fails, return `disconnected`, `invalid_auth`, `insufficient_scope`, `pending_approval`, `unavailable`, or `blocked`. Never imply that a draft was sent or a proposal was executed.

## MCP contracts

- `neyvro_get_capabilities` — discover tenant-scoped service implementation and action support.
- `neyvro_get_connections` — discover connected accounts and provider health without exposing credentials.
- `neyvro_get_permissions` — discover granted scopes and permission expiry.
- `neyvro_get_approval_status` — verify an exact action’s current approval and version.

These are read-only discovery contracts. Execution uses the separately authorized service contract named in the capability response; this skill never substitutes an undocumented or Chronos tool.

## Disconnected behavior

When no Neyvro account is available, continue with knowledge-only strategy, ICP, research planning, copy drafts, briefs, deterministic campaign specifications, SEO/GEO recommendations, and measurement definitions from user-supplied context. Label live records, connected-account facts, execution results, and performance measurements as unavailable.

See the exact skill selected by metadata search for domain instructions; related skills are hints, not an instruction to load the entire library.
