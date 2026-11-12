# MCP tool integration matrix

Source of truth: NEYVRO `mcp-bridge` commit `abe22e7`, specifically
`docs/integrations/mcp-bridge.md` and `mcp-bridge.openapi.json`.

Thirty private tools are callable when the bridge is configured. They reuse
fourteen read-only operations:

| Operation | Route | Scope | MCP tools |
|---|---|---|---|
| companies.search | GET `/v1/mcp/companies` | intelligence:read | search_companies |
| companies.get | GET `/v1/mcp/companies/{company_id}` | intelligence:read | get_company_twin, get_company_timeline, get_company_signals, get_evidence, get_monitoring_status |
| companies.people | GET `/v1/mcp/companies/{company_id}/people` | intelligence:read | get_opportunity_buyers, get_buyer, get_contact_verification |
| buyers.search | GET `/v1/mcp/buyers` | intelligence:read | search_buyers |
| signals.list | GET `/v1/mcp/signals` | intelligence:read | AWS operation available; no direct legacy MCP tool |
| opportunities.list | GET `/v1/mcp/opportunities` | intelligence:read | list_opportunities |
| opportunities.get | GET `/v1/mcp/opportunities/{opportunity_id}` | intelligence:read | explain_opportunity, opportunity_history, buying_window, qualification |
| objective.get | GET `/v1/mcp/objective` | intelligence:read | get_research_questions |
| brief.get | GET `/v1/mcp/brief` | intelligence:read | get_customer_context, get_icp, get_positioning, get_gtm_strategy |
| pipeline.get | GET `/v1/mcp/pipeline` | intelligence:read | get_pipeline |
| analytics.get | GET `/v1/mcp/analytics` | intelligence:read | No direct legacy MCP tool |
| conversations.list | GET `/v1/mcp/conversations` | mail:read | list_conversations, get_reply_status, get_followup_queue |
| conversations.get | GET `/v1/mcp/conversations/{conversation_id}` | mail:read | get_conversation |
| mail.overview | GET `/v1/mcp/mail/overview` | mail:read | get_connections, get_capabilities, get_permissions, get_sender_status, get_campaign_metrics |

Corrections: conversation lookup uses `conversation_id`; follow-up queue forces
`filter=waiting`; permissions expose only the caller's access; mailbox tools
use `mail:read`. The other 26 private tools stay disabled.

Disabled breakdown: 6 pending write/research contracts, 7 with no backend, 1
unsafe ICP evaluation, and 12 prohibited/provider-unavailable tools. No
disabled tool is registered in the callable private MCP server.
