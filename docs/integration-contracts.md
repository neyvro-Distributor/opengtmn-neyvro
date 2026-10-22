# Portable Neyvro Agent Plugin integration contracts

This document is the implementation contract for a portable plugin. It keeps
the existing FastAPI/PostgreSQL/Firebase architecture as the authority and
adds an adapter surface rather than duplicating domain services.

## Artifact layout

```text
plugin/
  skills/<neyvro-skill>/SKILL.md
  mcp/server.mjs                 # portable knowledge/discovery adapter
  manifest.json                   # client-neutral plugin metadata
  clients/codex.json
  clients/claude-code.json
  clients/cursor.json
  clients/chatgpt.json
```

The server may reuse the OpenGTM zero-dependency stdio pattern for local skill
knowledge, but Neyvro execution calls must be explicit HTTP calls to the
existing API or a separately deployed Neyvro MCP gateway. Do not import the
Chronos `geo_*` namespace or imply that it is available locally.

## Required MCP surface

### Discovery tools

- `neyvro_list_skills()` → `{ skills: [{ name, description, mode }] }`
- `neyvro_get_skill(name)` → `{ name, markdown, license, source }`
- `neyvro_search_skills(query)` → ranked skill summaries
- `neyvro_capabilities(workspace_id)` → capability/status matrix with provider state

### Read tools

- `neyvro_get_onboarding(workspace_id)`
- `neyvro_get_brief(workspace_id)`
- `neyvro_discover_companies(workspace_id, query, limit, cursor)`
- `neyvro_get_company(workspace_id, company_id)`
- `neyvro_get_evidence(workspace_id, subject_id, cursor)`
- `neyvro_get_investigation(workspace_id, case_id)`
- `neyvro_get_contacts(workspace_id, company_id, filters, cursor)`
- `neyvro_get_outreach_state(workspace_id, company_id)`
- `neyvro_get_analytics(workspace_id, range, dimensions)`

### Proposal and approval tools

- `neyvro_propose_draft(workspace_id, recipient, evidence_ids, content)`
- `neyvro_propose_sequence(workspace_id, contacts, steps, stop_conditions)`
- `neyvro_approve_action(workspace_id, request_id, confirmation_token)`
- `neyvro_send_approved_action(workspace_id, request_id, idempotency_key)`

There must be no direct `send`, `publish`, `launch`, or account mutation tool
without the proposal/approval boundary. The API's existing draft, approval,
mail operation, mailbox permission, and sequence routes are the likely adapter
targets.

## Common request envelope

```json
{
  "workspace_id": "uuid",
  "actor": { "session": "opaque-session-reference" },
  "request_id": "uuid",
  "idempotency_key": "client-generated-key",
  "input": {}
}
```

The gateway derives the authenticated user and workspace from the existing
Firebase/revocable session, then verifies membership and role. A caller-supplied
workspace ID is a selector, never proof of access.

## Common response envelope

```json
{
  "request_id": "uuid",
  "workspace_id": "uuid",
  "data": {},
  "evidence": [{ "id": "uuid", "source": "url", "observed_at": "RFC3339" }],
  "next_cursor": null,
  "warnings": []
}
```

Execution responses must include operation status, approval state, provider,
and idempotency result. Contact responses must include verification state and
source labels; unknown names/emails must be omitted rather than guessed.

## Authorization and safety contract

- Read tools require an authenticated workspace member and read scope.
- Draft/proposal tools require a member role and proposal scope.
- Send/publish/account-changing tools require owner/member authorization,
  explicit approval, mailbox/provider permission, and an idempotency key.
- Every database lookup must retain the existing workspace ownership predicate.
- Cross-workspace IDs return a non-disclosing not-found/forbidden response.
- Provider outages return `BLOCKED_PROVIDER` with no fabricated result.
- Reply detection must close or suppress open follow-up tasks before any later
  scheduled send is eligible.

## Client adapters

Codex and Claude Code can consume the Agent Skills directory plus stdio/HTTP
MCP. Cursor and other MCP clients can consume the same MCP server with a client
config adapter. ChatGPT support depends on the connected MCP/connector surface;
it must be tested against the actual client rather than assumed from a manifest.
All adapters must point to the same Neyvro gateway and must not duplicate
business logic.
