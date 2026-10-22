# Neyvro capability and gap analysis

Audit date: 2026-10-22. Repository inspected: `/Users/ankitpandey/neyvro/neyvro`
at commit `4dee606` (`Add Render API deployment blueprint`). The target plugin
repository is this repository, `opengtmn-neyvro-`, whose prior baseline had only
the license and the small foundation added in this session. No other
Neyvro-named Git repository was found in the workspace. Downloaded PDFs, ZIPs,
HTML exports, and prompts were treated as artifacts, not executable services.

Status meanings: IMPLEMENTED means source and tests exist; PARTIAL means a
bounded slice exists but a material part is absent or provider-dependent;
MISSING means no implementation was found; BLOCKED means implementation needs
an external contract, credential, or authorization not present in the workspace.

| Capability | Status | Evidence in actual source | Gap for plugin execution |
|---|---|---|---|
| Customer onboarding and ICP | IMPLEMENTED | `apps/api/app/onboarding/routes.py`, `service.py`, `schemas.py`; company/product/sales answers and versioned brief flow | Expose read/update as reviewed plugin resources; do not let a plugin bypass workspace roles or confirmation |
| Company discovery | IMPLEMENTED | `apps/api/app/discovery/routes.py`, `service.py`, `collect.py`, `research.py`, `providers.py`; Exa/Firecrawl are optional | Add stable tool schemas and provider-status/error contracts |
| Monitoring and evidence | IMPLEMENTED | `apps/api/app/operations/monitor.py`, `app/investigation/providers.py`, `models.py`, workers, evidence migrations | Add MCP resource pagination and source/evidence provenance schema |
| Digital twins | PARTIAL | Company profiles, research briefs, investigation context and versioned onboarding state exist; no explicit digital-twin aggregate/API was found | Define a read-only twin projection and freshness/confidence contract |
| Predictive opportunities | IMPLEMENTED | `apps/api/app/investigation/predictions.py`, `evaluation.py`, prediction migrations, prediction tests | Expose explanations and evidence IDs; keep predictions advisory, never proof of intent |
| Buyer intelligence | IMPLEMENTED | `apps/api/app/discovery/people.py`, `contacts.py`, `contact_service.py`, `enrichment.py`, and contact tests | Add a plugin-safe contact schema with verification/source labels and no invented identities |
| Email integrations | IMPLEMENTED | `apps/api/app/mail/routes.py`, `providers.py`, `sync.py`, `crypto.py`; Gmail/Microsoft callbacks, permissions and encryption | Map provider errors and connection lifecycle into MCP; require explicit send scope |
| Campaigns and follow-ups | PARTIAL | Mail send operations, drafts, sequence models/routes, follow-up tasks, reply classification and stop logic exist | No generic campaign abstraction equivalent to all OpenGTM/Chronos workflows; add proposal/approval/idempotency contract |
| CRM and analytics | PARTIAL | Workspace pipeline stages, operations views, opportunity notifications and prediction/operational metrics exist | No broad CRM connector or revenue attribution system was found; define read-only analytics contract first |

## Security findings relevant to the plugin

The existing API has Firebase identity verification, revocable sessions,
workspace membership, owner/member/viewer roles, origin checks, mailbox
permissions, encrypted mailbox credentials, and workspace-owned database models.
These are the source of truth. The plugin must call the API with the selected
workspace/session context; it must not create a second authorization system.

The API test suite was run with `cd apps/api && uv run pytest -q`:

```text
1046 passed in 130.77s (0:02:10)
```

That result verifies the current API suite, not MCP compatibility or external
provider availability. No claim of live provider connectivity is made here.
