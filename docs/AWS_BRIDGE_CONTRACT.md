# AWS bridge contract (NEYVRO API side)

> **Copy for the Render MCP adapter.** The source of truth is
> `docs/integrations/mcp-bridge.md` in the **neyvro** repository, branch
> `mcp-bridge`, commit `1668dea`. If the two differ, the neyvro copy wins.
> Paths such as `apps/api/...` and `ops/mcp/...` below are in the neyvro repository.
> This replaces the "pending" contract in [BACKEND_AUTH_BRIDGE.md](BACKEND_AUTH_BRIDGE.md)
> for phase 1: the AWS side is built and tested on that branch but is **not deployed**
> yet, so the live Render service must keep the backend adapter disabled until it is.

**Status:** built and tested on branch `mcp-bridge` only. **Not merged and not deployed.**
The AWS API and the live product are unchanged. Phase 1 has exactly one operation,
`companies.search`, which only reads. Sending, approving and campaign changes don't
exist in the bridge.

Code: `apps/api/app/integrations/mcp/`. Tests: `apps/api/tests/test_mcp_bridge.py`.
Local end-to-end tools: `ops/mcp/`.

---

## 1. Three tokens

Every MCP tool call uses three separate tokens. Each one has one sender, one
receiver and one job, and none of them is accepted anywhere else.

| | **Token A: Firebase ID token** | **Token B: gateway assertion** | **Token C: access token** |
|---|---|---|---|
| Proves | Who the person is | Render vouches for that person and says what it wants | The API allowed this person, workspace and operation |
| Signed by | Google (Firebase) | Render (ES256) | NEYVRO API (ES256) |
| Travels | MCP client → Render | Render → `POST /v1/integrations/mcp/exchange` | API → Render → that operation's `/v1/mcp/*` route |
| `typ` header | (Firebase) | `gateway+jwt` | `mcp-access+jwt` |
| Lifetime | 1 hour (Firebase) | 60 s at most, **single use** | 60 s, **one tool call** |
| Never goes to | the NEYVRO API | data routes | the MCP client, the AI, website routes |

## 2. One tool call

1. The MCP client calls a tool on Render with Token A.
2. Render verifies Token A (section 8).
3. Render makes a **fresh** Token B for this call.
4. Render sends it to `POST /v1/integrations/mcp/exchange`.
5. The API verifies Token B, uses up its `jti`, applies the permission policy and returns Token C.
6. Render calls the operation's route with Token C.
7. The API verifies Token C and checks the person's access again, live. It then returns only that workspace's data and audits the call.
8. Render returns the result to the client without any token.

Phase 1 rule: **one fresh B and one fresh C per tool invocation.** Don't cache C
across tool calls.

## 3. Token B (Render signs, the API checks)

**Header:** exactly these three fields. Anything else is refused, including `jku`,
`x5u`, `jwk`, `x5c` and `crit`.

```json
{"alg": "ES256", "typ": "gateway+jwt", "kid": "gw-1"}
```

| Claim | Required | Value | What the API checks |
|---|---|---|---|
| `iss` | yes | `neyvro-mcp-gateway` | exact match |
| `aud` | yes | `neyvro-mcp-exchange` | exact match, as a string (a list is refused) |
| `sub` | yes | the Firebase UID from Token A | 1–128 printable characters, no spaces. It must match exactly one `users.firebase_uid`; never matched by email. |
| `email_verified` | yes | `true` or `false`, copied from Token A | must be a boolean; `false` is refused (403) |
| `op` | yes | the operation, e.g. `companies.search` | defined in code **and** switched on |
| `scope` | yes | space-separated permissions the person granted (OAuth grant), e.g. `intelligence:read` | must include the operation's permission. Extras are ignored and never passed on. |
| `workspace_id` | no | lowercase UUID | a **request**, not proof: membership is checked |
| `iat`, `exp` | yes | numbers; `exp − iat` ≤ 60 | `iat` not in the future (5 s skew); not expired |
| `jti` | yes | a new lowercase UUID every time | used once, atomically; a second use is refused (401 `assertion_replayed`) |
| `client` | no | MCP client name, e.g. `claude`, `chatgpt` (`[a-z0-9._-]`, ≤ 64) | audit only, never used to decide anything |

Python (PyJWT) example for Render:

```python
token_b = jwt.encode(
    {
        "iss": "neyvro-mcp-gateway",
        "aud": "neyvro-mcp-exchange",
        "sub": firebase_uid,                 # from verified Token A
        "email_verified": email_verified,    # from verified Token A
        "op": "companies.search",
        "scope": "intelligence:read",        # what the person granted
        "workspace_id": workspace_id,        # optional
        "iat": now,
        "exp": now + 60,
        "jti": str(uuid.uuid4()),
        "client": "claude",                  # optional
    },
    gateway_private_key,
    algorithm="ES256",
    headers={"kid": "gw-1", "typ": "gateway+jwt"},
)
```

## 4. `POST /v1/integrations/mcp/exchange`

**Request:** `Authorization: Bearer <Token B>`, no body. No cookies and no `Origin`
are needed; they are ignored.

**200 response** (`Cache-Control: no-store`):

```json
{
  "access_token": "<Token C — for the NEYVRO API only, never show it to the AI>",
  "token_type": "Bearer",
  "expires_in": 60,
  "exchange_id": "1b0c7f4e-…",
  "operation": "companies.search",
  "scopes": ["intelligence:read"],
  "workspace": {"id": "cc38cc2c-…", "name": "Test Alpha"},
  "role": "owner"
}
```

**409 `choose_workspace`:** the person belongs to more than one active workspace and
Token B named none. Ask the person which one, then send a **new** Token B with
`workspace_id`.

```json
{"detail": {"code": "choose_workspace", "message": "…",
            "workspaces": [{"id": "…", "name": "Test Alpha", "role": "member"},
                           {"id": "…", "name": "Test Beta", "role": "member"}]}}
```

Every other refusal has the form `{"detail": {"code": "<code>", "message": "<text>"}}`.
Codes are in section 7.

## 5. Token C (the API signs and checks; Render treats it as opaque)

The header is `{"alg": "ES256", "typ": "mcp-access+jwt", "kid": "<API key id>"}`.

| Claim | Value |
|---|---|
| `iss` | `neyvro-api` |
| `aud` | `neyvro-mcp-api` |
| `sub` | the NEYVRO user ID (**not** the Firebase UID) |
| `workspace_id` | the one workspace allowed |
| `op` | the one operation allowed |
| `scope` | only the permission that operation needs |
| `iat`, `exp` | 60 s apart |
| `jti` | `exchange_id`, also recorded in the audit log |

Token C carries no email, name or role; the API reads those live. Render must not
decode Token C to make decisions: use the exchange response instead.

On **every** call the API checks:

- **The token itself:** `alg`, `typ`, `kid`, signature, `iss`, `aud`, lifetime and expiry.
- **The operation:** the route's operation equals `op`, and its permission is in `scope`.
- **The person, live:**
  - the user isn't disabled;
  - the membership isn't removed;
  - the account is active;
  - the role still allows the permission;
  - the operation is still switched on.

  So removing someone takes effect on their very next call.
- **Then:** the rate limit, followed by an audit row.

## 6. Operation `companies.search`

MCP tool `neyvro_search_companies` maps to:

```
GET /v1/mcp/companies?query=<text, optional, ≤100>&page=<1..10000, default 1>&page_size=<1..100, default 25>
Authorization: Bearer <Token C issued for companies.search>
```

It returns the workspace's ranked Discovery companies: the same list, in the same
order, as Discovery on the website. `query` keeps only companies whose name or domain
contains it (case-insensitive). The route only reads: it starts no research, spends no
credits and saves nothing (the request's transaction is rolled back after reading).

```json
{
  "workspace_id": "cc38cc2c-…",
  "operation": "companies.search",
  "query": "talent",
  "page": 1,
  "page_size": 25,
  "total": 1,
  "companies": [
    {
      "company_id": "…",
      "rank": 1,
      "name": "TalentLoop",
      "domain": "talentloop.example",
      "score": 82,
      "fit": 4, "timing": 3, "evidence": 4,
      "label": "strong", "verdict": null, "status": "assessed",
      "tracked": false, "pipeline_stage": "new", "is_new": true,
      "summary": "…", "why_now": "…",
      "reasons": [{"tone": "plus", "text": "…"}],
      "assessed_at": "2026-11-10T18:36:50Z"
    }
  ]
}
```

(Values above are illustrative; fields and types are exact.) `rank` is the position
in the full ranked list, before `query` filters it.

## 7. Error codes

| HTTP | `code` | Meaning | What the gateway should do |
|---|---|---|---|
| 503 | `bridge_unavailable` | Bridge switched off or keys missing/unusable | Tell the person the NEYVRO tools are unavailable |
| 401 | `missing_token` | No `Authorization: Bearer` (or longer than 4096 characters) | Fix the request |
| 401 | `invalid_assertion` | Token B failed a check: header, key, signature, claims or lifetime | Don't retry the same token; check signing |
| 401 | `assertion_expired` | Token B expired | Make a new one |
| 401 | `assertion_replayed` | This Token B was already used | Make a new one; never reuse |
| 401 | `invalid_token` | Token C failed a check | Exchange again |
| 401 | `token_expired` | Token C expired | Exchange again |
| 401 | `unknown_user` | No NEYVRO account has this Firebase UID | Ask the person to sign up for NEYVRO |
| 403 | `user_disabled` | The NEYVRO account is disabled | Stop |
| 403 | `email_unverified` | `email_verified` is false | Ask the person to verify their email |
| 403 | `operation_not_allowed` | Operation not defined or not switched on | Don't offer the tool |
| 403 | `operation_mismatch` | Token C was issued for another operation | Exchange for this operation |
| 403 | `scope_not_granted` | The grant lacks the operation's permission | Ask the person to grant it |
| 403 | `role_not_allowed` | The person's role can't do this | Stop |
| 403 | `workspace_forbidden` | Not this person's workspace, or it doesn't exist (same answer either way) | Stop |
| 403 | `account_inactive` | The workspace's account is suspended or closed | Stop |
| 403 | `no_workspace` | The person has no active workspace | Stop |
| 403 | `not_a_member` | Membership removed after Token C was issued | Stop |
| 409 | `choose_workspace` | Several workspaces; see the list | Ask, then send a new Token B with `workspace_id` |
| 429 | `rate_limited` | Limit reached (`Retry-After: 60`) | Wait a minute |
| 422 | (FastAPI) | Bad query parameters | Fix the request |

401 responses carry `WWW-Authenticate: Bearer error="invalid_token"`.

## 8. What Render must do (gateway side)

1. **Verify Token A fully:**
   - Algorithm and key: `alg` RS256 only, with the `kid` taken from Google's keys at
     `https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com`.
   - Issuer and audience: `iss` `https://securetoken.google.com/<project>` and `aud` `<project>`.
   - Time: `exp`, `iat` and `auth_time`.
   - Identity: a non-empty `sub`.
2. **Check revocation and disabled accounts:** use the Firebase Admin SDK
   (`verify_id_token(token, check_revoked=True)`) with a service account, a short
   timeout, and **fail closed** if Firebase is unreachable. Signing out in the client
   doesn't revoke tokens that were already issued.
3. **Email policy:** copy `email_verified` from Token A into Token B. The API refuses
   `false`, so test users must have verified emails (section 10).
4. **Never forward Token A** to the NEYVRO API, and never put it inside Token B.
5. **One fresh Token B and Token C per tool invocation:** a new `jti` every time, and no
   caching of C across calls.
6. **Never show Token C** to the AI or the MCP client, and never log any token.
7. **Fixed API address:** the NEYVRO API base URL comes from configuration only. No
   claim, header or tool argument may choose or change it.
8. **External MCP clients** (ChatGPT, Claude and others) need MCP OAuth access tokens
   with resource-audience validation, scopes and PKCE. The Firebase ID token is a
   first-party compatibility mode only. Put the scopes the person granted into Token B's
   `scope`; the API never grants more than that **and** never more than the person's
   role allows.
9. **SDK version:** pin the MCP SDK version you deploy (`mcp>=1.0.0,<2` floats today).
   The bridge is plain HTTPS + JSON and doesn't depend on the MCP protocol version, so the
   existing handshake doesn't need to change.

## 9. Permission policy (`app/integrations/mcp/policy.py`)

- **The API decides.** Render only says who the person is.
- **Default deny:** anything not listed is refused.

| Permission | Meaning | Viewer | Member | Owner | Used by an operation now |
|---|---|---|---|---|---|
| `intelligence:read` | Read saved research | ✓ | ✓ | ✓ | `companies.search` |
| `mail:read` | Own mailboxes' conversations | ✓ | ✓ | ✓ | no |
| `proposals:write` | Drafts only; nothing approved or sent | ✗ | ✓ | ✓ | no |
| `research:run` | Research that spends credits | ✗ | ✓ | ✓ | no |

**Never granted through MCP, whatever the role or the request:**
- `messages:send`, `approvals:write`, `followups:write`
- `mailboxes:write`, `members:write`, `billing:write`
- `account:write`, `privacy:write`, `admin:write`

If a gateway asks for one of these, it is recorded in the audit log as
`never_granted_requested`.

**Workspace rules:**
- Only live memberships count; a pending invitation is not a membership.
- The account must be `active`.
- NEYVRO staff roles add nothing.
- One workspace per Token C.

**Records:** every query is filtered by Token C's workspace.

## 10. Configuration (API side)

All of these are off or empty by default. **Off, or on without both keys, every
bridge route answers 503.**

| Variable | Default | Meaning |
|---|---|---|
| `NEYVRO_MCP_BRIDGE_ENABLED` | `false` | Master switch |
| `NEYVRO_MCP_GATEWAY_PUBLIC_KEYS` | — | JSON `{"<kid>": "<PEM public key>"}`, 1–5 EC P-256 keys (two during rotation) |
| `NEYVRO_MCP_SIGNING_KEY` | — | The API's own EC P-256 private key (PEM; `\n` escapes accepted) that signs Token C |
| `NEYVRO_MCP_SIGNING_KEY_ID` | `aws-1` | `kid` of Token C |
| `NEYVRO_MCP_GATEWAY_ISSUER` | `neyvro-mcp-gateway` | Token B `iss` |
| `NEYVRO_MCP_EXCHANGE_AUDIENCE` | `neyvro-mcp-exchange` | Token B `aud` |
| `NEYVRO_MCP_TOKEN_ISSUER` | `neyvro-api` | Token C `iss` |
| `NEYVRO_MCP_TOKEN_AUDIENCE` | `neyvro-mcp-api` | Token C `aud` |
| `NEYVRO_MCP_ASSERTION_MAX_SECONDS` | `60` | Longest Token B lifetime accepted |
| `NEYVRO_MCP_TOKEN_SECONDS` | `60` | Token C lifetime |
| `NEYVRO_MCP_CLOCK_SKEW_SECONDS` | `5` | Clock tolerance |
| `NEYVRO_MCP_EXCHANGES_PER_MINUTE` | `60` | Per person (counted per Firebase UID) |
| `NEYVRO_MCP_CALLS_PER_MINUTE` | `60` | Per workspace |
| `NEYVRO_MCP_OPERATIONS` | `companies.search` | Operations switched on; only names defined in code count |

**Keys.** The gateway and the API must use different keys and key IDs; the API
refuses to start the bridge otherwise.

- **Render:** makes its own key pair and keeps the private key only in its secret settings.
- **NEYVRO:** receives the **public** key only.
- **The API's own key:** made separately and kept only in the API's secret store.

```bash
openssl ecparam -name prime256v1 -genkey -noout -out key.pem   # private: keep secret
openssl ec -in key.pem -pubout -out key.pub.pem                # public: safe to share
```

**Rotation:**
1. Add the new public key under a new `kid` next to the old one.
2. Switch Render to the new key.
3. Remove the old key.

Rotate every 90 days, or immediately after a leak.

**Testing and live never mix:**

| | Testing | Live (only after go-live) |
|---|---|---|
| Firebase project | a separate test project (e.g. `neyvro-mcp-test`), which doesn't exist yet; create it | `neyvro-79e95` |
| Gateway key | `gw-test-1` | `gw-1` |
| API key | `aws-test-1` | `aws-1` |
| API address | `http://127.0.0.1:8001` | the AWS link |

**Firebase test users:**
- Create them in the **test** project.
- Mark their emails verified, for example with the Admin SDK
  `auth.update_user(uid, email_verified=True)` or by clicking the verification email.
- Seed the isolated database with their real UIDs:
  `seed_test_data.py --uid alpha-owner=<UID> …`.

## 11. Replay protection, limits and audit

**Replay protection.** The `jti` is inserted with `INSERT … ON CONFLICT DO NOTHING`,
so of any number of simultaneous exchanges of one Token B, exactly one passes.
- The claim is committed before the person is checked, so a refused Token B is used up too.
- Rows are deleted a day after the token expires.

**Limits.** Counted with one `INSERT … ON CONFLICT DO UPDATE` per request in
`mcp_rate_counters`. Every API process shares the count, and simultaneous requests are
counted exactly; no Redis is needed. The window is one minute.

**Audit.** These actions are written to `audit_logs`, which is append-only:
- `mcp.exchange` and `mcp.call` for allowed requests;
- `mcp.exchange_denied` and `mcp.call_denied` for refusals, with `reason`.

Each row records:
- `exchange_id`, `gateway_jti` and the gateway `key_id`;
- the operation, the client and the request ID;
- the subject as a SHA-256 hash.

**What is never recorded:** no token is ever stored or logged. Tokens that fail signature
or format checks are logged as warnings, not audited, because they didn't come from the
gateway.

## 12. Running it locally (isolated; never touches AWS or the development database)

```bash
# 1. A separate copy of the repository on branch mcp-bridge
git worktree add ../neyvro-mcp-bridge mcp-bridge
# 2. A separate Postgres on 127.0.0.1:5440 (own data folder), empty database neyvro_mcp_dev
#    .env in the copy: NEYVRO_DATABASE_URL=…@127.0.0.1:5440/neyvro_mcp_dev plus TEST keys
cd ../neyvro-mcp-bridge/apps/api && uv sync --locked && uv run alembic upgrade head
# 3. Made-up people (refuses any database that isn't local, port ≠ 5433, *_mcp_dev)
uv run python ../../ops/mcp/seed_test_data.py
# 4. The copy's API
uv run uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8001
# 5. Play the gateway (refuses any address other than 127.0.0.1/localhost)
uv run python ../../ops/mcp/local_check.py --api http://127.0.0.1:8001 \
    --key <gateway TEST private key> --kid gw-test-1
# Tests (throwaway databases on the same isolated server)
uv run pytest tests/test_mcp_bridge.py
```

## 13. Going live (not done; only when the owner says so)

1. Merge `mcp-bridge` into `main`.
2. Make **new** production keys (`gw-1` on Render, `aws-1` for the API).
3. Add the `NEYVRO_MCP_*` secret names to `app_secret_keys` in
   `infra/aws/production.tfvars`. Run `terraform plan`, review it, then `apply`.
4. Set the values with `ops/aws/put-app-secret.py`.
5. Deploy with the switch **off**. The migration adds only `0065`, which creates two new tables.
6. Switch it on. Test with two **new** test accounts, then delete them.
7. To undo: switch it off and restart the API. Every bridge route answers 503 and nothing
   else is affected.
