---
name: lead-sourcing-and-enrichment
description: Activate when selecting ICP-fit accounts, finding buyer roles, or enriching authorized business contacts with deduplicated, provenance-labeled, verified data.
license: MIT
metadata:
  version: 0.2.0
  maturity: playbook
  mode: research
  required_scopes: ["intelligence:read"]
  related_skills: ["ideal-customer-profile", "account-research", "evidence", "buyer-matching", "email-deliverability"]
---

# Lead sourcing and enrichment

Turn an approved ICP into a clean, reviewable buyer list. Select accounts first, infer roles second, then enrich contacts through a bounded waterfall. A discovered person is not automatically a reachable lead: identity, company match, provenance, verification, freshness, permitted use, suppression, and entitlement must all be explicit.

## Operating modes

- **Knowledge-only:** explain sourcing, verification, or list-hygiene methods without login, provider calls, or real-person claims.
- **Connected research:** read authorized ICP, company, opportunity, CRM, suppression, and provider results. Return unknowns when a service is unavailable.
- **Draft-only:** produce a proposed target list or enrichment plan. Never create a CRM record, enroll a sequence, or send a message.
- **External action:** requires tenant scope, provider permission, customer entitlement, usage budget, explicit approval, audit logging, and an idempotency key.

## Discovery workflow

1. Apply the customer-approved ICP to companies. Exclude existing customers, active opportunities, suppressed accounts, competitors, and accounts with a disqualifier before searching for people.
2. Infer the buying committee from the problem and approved persona model: economic buyer, champion, user, technical evaluator, approver, and blocker. Role inference is a hypothesis until a source verifies the current role.
3. Match existing CRM and opportunity contacts before paying a provider. Reuse a fresh authorized contact record; do not create duplicates for a changed title or alternate spelling.
4. Use a waterfall from the lowest-cost authorized source to the next provider. Stop after a verified hit or when the customer budget/rate limit is exhausted. Paid enrichment is disabled without explicit entitlement and remaining usage budget.
5. Verify company identity and current employment together. A contact from a similarly named or former company is a `wrong_company` exclusion, not a usable match.
6. Verify email separately from identity. `verified` means the provider or verification service confirmed the address; a guessed/pattern-generated address is never verified. Catch-all, unknown, risky, invalid, bounced, and unverified states remain non-verified.
7. Normalize and deduplicate by provider person ID, normalized email, and `(name, company domain, current role)` fallback. Preserve all source references and the strongest verification history.
8. Check global/workspace suppression, opt-outs, existing-customer exclusions, and permitted-use constraints before returning a contact. Never expose private personal data or scrape a platform against its rules.

## Contact contract

For every discovered person return:

```json
{
  "name": "Alex Morgan",
  "company": "Example Inc",
  "current_role": "VP Engineering",
  "buyer_category": "economic_buyer|champion|user|technical_evaluator|approver|blocker|unknown",
  "source": {"provider": "crm|provider-name", "record_id": "...", "url": "..."},
  "verification_status": "verified|unverified|catch_all|invalid|stale|opted_out|wrong_company",
  "last_verified_at": "2026-10-20T00:00:00Z",
  "opportunity_ids": ["opportunity-123"],
  "contact_details": {
    "email": "alex@example.com",
    "email_provenance": "provider_verified|crm_verified|pattern_guess|unknown",
    "permitted_use": true,
    "permitted_use_basis": "workspace policy or provider terms"
  }
}
```

Email and phone fields require source, observed time, verification result, and permitted-use basis. A pattern guess may be returned only as `unverified` when the workflow explicitly allows it; never use it as proof of identity or deliverability.

## Budgets, freshness, and failure behavior

- Track `provider_calls`, `paid_calls`, `units_consumed`, `units_remaining`, and per-provider rate-limit state.
- Do not call a paid provider if `entitled` is false, the usage budget is exhausted, or the provider has no permitted-use basis.
- Default contact freshness is 30 days unless the customer or provider supplies a stricter window. A stale record must be re-verified or marked `stale`; it must not silently become current.
- Provider timeout, quota, auth, policy, or malformed-response failures are recorded as provider events and do not become guessed data. Continue to the next authorized waterfall step only when its budget and policy allow.
- Opt-outs and suppression are hard stops. Existing customers and active opportunities are excluded by default; a customer-approved exception must be explicit and auditable.

## MCP contracts

Use authenticated, tenant-scoped adapters with `intelligence:read`:

- `neyvro_search_buyers` — search ICP-filtered accounts and buyer roles.
- `neyvro_get_opportunity_buyers` — read existing opportunity contacts and relationship context.
- `neyvro_enrich_contact` — run bounded waterfall enrichment; paid calls require entitlement and usage budget.
- `neyvro_get_contact_verification` — read verification, freshness, provenance, opt-out, and permitted-use state.

The skill prefers existing Neyvro buyer/CRM services and does not create a duplicate contact database. Provider adapters must use approved B2B APIs or first-party CRM data, respect provider terms, and never scrape prohibited platforms.

## Structured result

Return `accounts_considered`, `accounts_excluded`, `contacts`, `duplicates_removed`, `suppressed_contacts`, `provider_events`, `usage`, and `research_gaps`. Include a sample result even in knowledge-only mode, with fictional values clearly marked as examples. A contact is eligible for downstream outreach only when `verification_status` is `verified`, `permitted_use` is true, and no suppression or existing-customer exclusion applies.

See also: `ideal-customer-profile` for fit, `account-research` for account signals, `buyer-matching` for role hypotheses, and `email-deliverability` for sending controls.
