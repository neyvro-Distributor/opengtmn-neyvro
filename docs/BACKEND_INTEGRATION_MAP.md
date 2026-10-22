# Backend integration map

| Capability | MCP surface | Existing implementation | Status |
|---|---|---|---|
| Onboarding/customer context | `neyvro_get_customer_context` | `/v1/onboarding` mapping | PARTIAL |
| ICP and fit | `neyvro_get_icp`, `neyvro_evaluate_icp_fit` | Onboarding/ICP local contracts | PARTIAL |
| Positioning/GTM | `neyvro_get_positioning`, `neyvro_get_gtm_strategy` | Local strategy modules | PARTIAL |
| Company discovery | `neyvro_search_companies` | Discovery route mapping | PARTIAL |
| Twin/timeline/signals/evidence | Four company tools | Read-only contracts | PARTIAL |
| Monitoring/opportunities | Monitoring, history, window, opportunity tools | Contract-only route mappings | PARTIAL |
| Buyers and contacts | Search/get/enrich/verification tools | Local validation and provider abstractions | BLOCKED |
| Drafting/personalization | Research and draft tools | Local draft modules | PARTIAL |
| Campaigns | Proposal/draft/status/state tools | Deterministic sequence/state logic | PARTIAL |
| Conversations | Conversation/reply/follow-up tools | Local classifier/stop logic | PARTIAL |
| Connections | Capability/connection/permission/sender tools | Mail route mapping | PARTIAL |
| Pipeline/analytics | Pipeline/qualification/metrics/attribution | Local metric contracts | DISABLED/PARTIAL |
| SEO/GEO | Audit/recommendation/proposal tools | Bounded optional analyzers | DISABLED |
| Content | Ideas/brief/draft/social proposal tools | Draft/proposal modules | DISABLED |

The MCP gateway is an adapter boundary; it does not create a second customer
database or intelligence engine. Live status remains limited by missing
provider credentials, backend service authentication, and deployment.
