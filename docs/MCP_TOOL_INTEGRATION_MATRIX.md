# MCP tool integration matrix

Audit basis: the 56 private tool specifications in `src/neyvro/remote_mcp.py`,
the existing local registry and skill definitions, and the AWS bridge contract
at `docs/AWS_BRIDGE_CONTRACT.md` (`neyvro` `mcp-bridge` commit `1668dea`). The
AWS contract defines exactly one operation: `companies.search`.

`READY_TESTED` means an allowlisted adapter exists and is covered by mocked
contract tests. A legacy path or a plausible endpoint name is not evidence of
an AWS integration. All rows except the first remain disabled and are not
registered as callable private MCP tools.

| Tool | Existing behavior / input | AWS operation / route | Scope | Side effects, cost, isolation | Flag / tests | Status / blocker |
|---|---|---|---|---|---|---|
| `neyvro_search_companies` | Company search; `query` ≤100, `page` 1..10000, `page_size` 1..100 | `companies.search`; `GET /v1/mcp/companies` | `intelligence:read` | Read-only, no credits; Token C workspace filter | `NEYVRO_MCP_BRIDGE_ENABLED`; `tests/test_remote_mcp.py` | **READY_TESTED** |
| `neyvro_get_company_twin` | Company read; `company_id` | None contracted; legacy `/v1/discovery/companies/{company_id}` | `intelligence:read` | Read intent, but no contracted workspace-bound route | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_get_company_timeline` | Timeline read; `company_id` | None contracted; legacy discovery route | `intelligence:read` | Read intent; no contracted route | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_get_company_signals` | Signals read; `company_id` | None contracted; legacy discovery route | `intelligence:read` | Read intent; no contracted route | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_get_evidence` | Evidence read; `company_id` | None contracted; legacy discovery route | `intelligence:read` | Read intent; no contracted route | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_get_monitoring_status` | Monitoring read; `company_id` | None contracted; legacy discovery route | `intelligence:read` | Read intent; no contracted route | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_list_opportunities` | Opportunity list | None contracted; legacy `/v1/accounts` | `intelligence:read` | Read intent; workspace filtering unverified | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_explain_opportunity` | Opportunity explanation; `opportunity_id` | None contracted; legacy account route | `intelligence:read` | Read intent; workspace filtering unverified | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_get_research_questions` | Research-question read | None contracted; legacy accounts route | `intelligence:read` | Read intent; no contract | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_get_opportunity_history` | History read; `opportunity_id` | None contracted; legacy account route | `intelligence:read` | Read intent; no contract | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_get_buying_window` | Buying-window read; `opportunity_id` | None contracted; legacy account route | `intelligence:read` | Read intent; no contract | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_get_customer_context` | Customer context read | None contracted; legacy onboarding route | `intelligence:read` | Read intent; no contract | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_get_icp` | ICP read | None contracted; legacy onboarding route | `intelligence:read` | Read intent; no contract | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_evaluate_icp_fit` | ICP evaluation | None contracted; legacy discovery route | `intelligence:read` | Evaluation may trigger research/cost; no budget contract | Bridge allowlist; no adapter test | **UNSAFE_MAPPING** |
| `neyvro_get_positioning` | Positioning read | None contracted; legacy onboarding route | `intelligence:read` | Read intent; no contract | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_get_gtm_strategy` | GTM strategy read | None contracted; legacy analysis route | `intelligence:read` | Read intent; no contract | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_search_buyers` | Buyer search | None contracted; legacy discovery route | `intelligence:read` | Read intent; no contract | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_get_opportunity_buyers` | Buyer list; `company_id` | None contracted; legacy discovery route | `intelligence:read` | Workspace and privacy policy unverified | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_get_buyer` | Buyer profile; `company_id` | None contracted; legacy discovery route | `intelligence:read` | Workspace and privacy policy unverified | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_enrich_contact` | Contact enrichment; `company_id` | None contracted; legacy POST route | `intelligence:read` | Research/provider cost possible; unsafe without budget/idempotency | Bridge allowlist; no adapter test | **UNSAFE_MAPPING** |
| `neyvro_get_contact_verification` | Verification read; `company_id` | None contracted; legacy contacts route | `intelligence:read` | Provider/privacy contract absent | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_research_account` | Account research; `company_id` | None contracted; legacy discovery route | `intelligence:read` | May spend credits; must require `research:run` and budget | Bridge allowlist; no adapter test | **UNSAFE_MAPPING** |
| `neyvro_research_buyer` | Buyer research; `company_id` | None contracted; legacy outreach route | `intelligence:read` | May spend credits; must require `research:run` and budget | Bridge allowlist; no adapter test | **UNSAFE_MAPPING** |
| `neyvro_draft_email` | Email draft; `company_id` | None contracted; legacy outreach-context route | `intelligence:read` | Draft-only intent; provider/content contract absent | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_draft_linkedin_message` | LinkedIn draft | None contracted | `intelligence:read` | Unofficial LinkedIn automation prohibited | No adapter flag; disabled test | **PROVIDER_UNAVAILABLE** |
| `neyvro_validate_outreach_claims` | Claims validation; `company_id` | None contracted; legacy outreach route | `intelligence:read` | Evidence/privacy contract absent | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_propose_campaign` | Campaign proposal; `campaign_id` | None contracted; legacy POST route | `intelligence:read proposals:write` | Campaign mutation/proposal; no contract | Disabled by policy; disabled test | **INTENTIONALLY_DISABLED** |
| `neyvro_create_campaign_draft` | Campaign draft; `campaign_id` | None contracted; legacy PUT route | `intelligence:read proposals:write` | Draft mutation; no AWS draft contract | Disabled by policy; disabled test | **INTENTIONALLY_DISABLED** |
| `neyvro_get_campaign` | Campaign read; `campaign_id` | None contracted; legacy mail route | `intelligence:read` | Read intent; no contract | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_list_campaigns` | Campaign list | None contracted; legacy accounts route | `intelligence:read` | Read intent; no contract | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_get_campaign_status` | Campaign status; `campaign_id` | None contracted; legacy mail route | `intelligence:read` | Read intent; no contract | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_submit_campaign_for_approval` | Approval submission; `campaign_id` | None contracted; legacy approval route | `intelligence:read proposals:write` | Approval side effect prohibited | Disabled by policy; disabled test | **INTENTIONALLY_DISABLED** |
| `neyvro_pause_campaign` | Pause campaign; `campaign_id` | None contracted; legacy mutation route | `intelligence:read proposals:write` | Campaign mutation prohibited | Disabled by policy; disabled test | **INTENTIONALLY_DISABLED** |
| `neyvro_resume_campaign` | Resume campaign; `campaign_id` | None contracted; legacy mutation route | `intelligence:read proposals:write` | Campaign mutation prohibited | Disabled by policy; disabled test | **INTENTIONALLY_DISABLED** |
| `neyvro_cancel_campaign` | Cancel campaign; `campaign_id` | None contracted; legacy mutation route | `intelligence:read proposals:write` | Campaign mutation prohibited | Disabled by policy; disabled test | **INTENTIONALLY_DISABLED** |
| `neyvro_list_conversations` | Conversation list; `company_id` | None contracted; legacy mailbox route | `mail:read` required by future contract | Mailbox privacy; no mailbox-level contract | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_get_conversation` | Conversation detail; `company_id` | None contracted; legacy mailbox route | `mail:read` required by future contract | Mailbox privacy; no mailbox-level contract | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_get_reply_status` | Reply status; `company_id` | None contracted; legacy mailbox route | `mail:read` required by future contract | Mailbox privacy; no contract | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_get_followup_queue` | Follow-up queue read | None contracted; legacy accounts route | `mail:read` required by future contract | Mailbox/workspace privacy; no contract | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_draft_reply` | Reply draft; `company_id` | None contracted; legacy mailbox route | `mail:read proposals:write` future policy | Draft-only; mailbox and draft contract absent | Disabled by policy; no adapter test | **MISSING_BACKEND** |
| `neyvro_get_capabilities` | Mail connection capabilities | None contracted; legacy connections route | `mail:read` required by future contract | Provider/account privacy; no contract | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_get_connections` | Mail connections | None contracted; legacy connections route | `mail:read` required by future contract | Provider/account privacy; no contract | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_get_permissions` | Mail permissions; `company_id` | None contracted; legacy connections route | `mail:read` required by future contract | Provider/account privacy; no contract | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_get_sender_status` | Sender status | None contracted; legacy connections route | `mail:read` required by future contract | Provider/account privacy; no contract | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_get_pipeline` | Pipeline read | None contracted; legacy accounts route | `intelligence:read` | Workspace isolation unverified | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_get_qualification` | Qualification read; `opportunity_id` | None contracted; legacy account route | `intelligence:read` | Read intent; no contract | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_get_revenue_attribution` | Revenue attribution read | None contracted | `intelligence:read` | Analytics backend absent | Disabled; catalog-only test | **MISSING_BACKEND** |
| `neyvro_get_campaign_metrics` | Campaign metrics read | None contracted; legacy metrics route | `intelligence:read` | Workspace analytics unverified | Bridge allowlist; catalog-only test | **MISSING_BACKEND** |
| `neyvro_analyze_website` | Website analysis; payload URL | None contracted | `research:run` required by future policy | Provider/SSRF/cost controls absent | Disabled; no adapter test | **PROVIDER_UNAVAILABLE** |
| `neyvro_get_seo_recommendations` | SEO recommendations | None contracted | `intelligence:read` | Provider/backend absent | Disabled; catalog-only test | **PROVIDER_UNAVAILABLE** |
| `neyvro_get_geo_recommendations` | GEO recommendations | None contracted | `intelligence:read` | Provider/backend absent | Disabled; catalog-only test | **PROVIDER_UNAVAILABLE** |
| `neyvro_propose_seo_changes` | SEO proposal | None contracted | `intelligence:read proposals:write` | Proposal/mutation absent | Disabled by policy; disabled test | **INTENTIONALLY_DISABLED** |
| `neyvro_generate_content_ideas` | Content ideas | None contracted | `intelligence:read` | Content service absent | Disabled; catalog-only test | **MISSING_BACKEND** |
| `neyvro_create_content_brief` | Content brief | None contracted | `intelligence:read` | Content service absent | Disabled; catalog-only test | **MISSING_BACKEND** |
| `neyvro_draft_content` | Content draft | None contracted | `intelligence:read proposals:write` future policy | Draft service absent | Disabled; catalog-only test | **MISSING_BACKEND** |
| `neyvro_propose_social_post` | Social post proposal | None contracted | `intelligence:read proposals:write` | Social provider/mutation absent | Disabled by policy; disabled test | **PROVIDER_UNAVAILABLE** |

## Count summary

- Private tools discovered: **56**.
- Verified callable adapters: **1** (`neyvro_search_companies`).
- Remaining private tools callable: **0**.
- The 55 unsupported tools remain disabled; registry presence is not counted as functionality.
