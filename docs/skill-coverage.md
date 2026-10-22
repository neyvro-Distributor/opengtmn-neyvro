# OpenGTM to Neyvro skill coverage

Neyvro currently has backend modules, not portable `SKILL.md` files. The
`neyvro-*` names below are proposed plugin skill identifiers; they are not
claimed to exist until the corresponding files are added and validated.

| OpenGTM skill | Neyvro skill mapping | Neyvro backend tools/contracts needed | Status |
|---|---|---|---|
| `gtm-strategy` | `neyvro-gtm-strategy` | onboarding state/brief read; analysis report read; proposal creation | PARTIAL |
| `ideal-customer-profile` | `neyvro-icp` | `/v1/onboarding`, `/v1/analysis`; versioned brief and buyer-role schema | IMPLEMENTED backend / MISSING plugin |
| `positioning-and-messaging` | `neyvro-positioning` | onboarding product answers; analysis report; approved personalization context | PARTIAL |
| `account-research` | `neyvro-account-research` | discovery company detail; research run; evidence/source projection | IMPLEMENTED backend / MISSING plugin |
| `lead-sourcing-and-enrichment` | `neyvro-contact-discovery` | people/contact search; enrichment providers; verification/source labels | IMPLEMENTED backend / MISSING plugin |
| `cold-email-writing` | `neyvro-message-drafting` | outreach context; draft create/update/version; provider-independent message schema | PARTIAL |
| `email-deliverability` | `neyvro-mail-deliverability` | mailbox connection status; provider permissions; send-operation status | PARTIAL |
| `linkedin-outreach` | `neyvro-social-outreach` | No Neyvro LinkedIn connector found; require provider contract and policy gate | BLOCKED |
| `multichannel-sequences` | `neyvro-follow-up-sequences` | sequence create/pause/resume; follow-up tasks; reply stop transition; idempotency key | PARTIAL |
| `outreach-personalization` | `neyvro-personalization` | research evidence; outreach context; draft versions; no fabricated fields | PARTIAL |
| `reply-handling-and-objections` | `neyvro-reply-intelligence` | message sync; reply classification; reply draft; approve/send; stop follow-ups | IMPLEMENTED backend / MISSING plugin |
| `discovery-and-qualification` | `neyvro-opportunity-qualification` | investigation case; evidence; objective; pipeline stage; feedback | PARTIAL |
| `seo-fundamentals` | `neyvro-seo-audit` | No SEO crawler/publisher route found; define read-only audit contract | MISSING |
| `generative-engine-optimization` | `neyvro-geo-audit` | No GEO crawler/publisher route found; require site-analysis provider | MISSING |
| `content-marketing-engine` | `neyvro-content-planning` | No content/social publishing backend found; proposal-only contract initially | MISSING |
| `outbound-metrics-and-benchmarks` | `neyvro-outbound-analytics` | operations metrics; campaign/send/reply aggregates; explicit denominators | PARTIAL |
| `gtm-automation-with-chronos` | `gtm-automation-with-neyvro` compatibility bridge | Neyvro MCP capability discovery; approval and scope contract; no Chronos tool proxy | IMPLEMENTED plugin bridge |
| `gtm-automation-with-neyvro` | `gtm-automation-with-neyvro` | `neyvro_get_capabilities`, `neyvro_get_connections`, `neyvro_get_permissions`, `neyvro_get_approval_status`; server-side gates for named services | IMPLEMENTED plugin bridge |
| `company-digital-twin-analysis` | `company-digital-twin-analysis` | `neyvro_get_company_twin`, `neyvro_get_company_timeline`, `neyvro_get_company_signals`, `neyvro_get_evidence` | IMPLEMENTED plugin / read-only adapter |
| `technology-change-detection` | `technology-change-detection` | company twin, signals, timeline, evidence | IMPLEMENTED plugin / read-only adapter |
| `predictive-problem-intelligence` | `predictive-problem-intelligence` | signals, predictive opportunities, ICP fit, evidence | IMPLEMENTED plugin / hypothesis-only |
| `evidence-verification` | `evidence-verification` | evidence, timeline, signals | IMPLEMENTED plugin / read-only adapter |
| `buying-window-detection` | `buying-window-detection` | buying windows, signals, timeline, evidence | IMPLEMENTED plugin / read-only adapter |
| `buyer-opportunity-matching` | `buyer-opportunity-matching` | buyer search, opportunity buyers, buying committee, evidence | IMPLEMENTED plugin / read-only adapter |
| `continuous-account-investigation` | `continuous-account-investigation` | investigation status, timeline, evidence, bounded company research | IMPLEMENTED plugin / job gated |
| `negative-evidence-analysis` | `negative-evidence-analysis` | negative evidence, evidence, signals, ICP fit | IMPLEMENTED plugin / read-only adapter |
| `revenue-attribution` | `revenue-attribution` | revenue attribution, pipeline, campaign metrics, evidence | IMPLEMENTED plugin / read-only adapter |

## Mapping rule

Knowledge skills may be loaded without external access. Execution skills must
resolve to a real Neyvro API capability, show tenant/workspace scope, carry
source/evidence IDs where applicable, and require approval for any send,
publish, or account-changing action. A documented OpenGTM `geo_*` name is not a
Neyvro backend tool unless an actual Neyvro route/service implementation exists.
