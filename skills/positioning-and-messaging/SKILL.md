---
name: positioning-and-messaging
description: Activate when developing, reviewing, or refining product positioning, value propositions, battlecards, buyer messaging, or approved message-house claims.
version: 0.2.0
maturity: playbook
mode: draft
required_scopes: [intelligence:read, proposals:write]
related_skills: [gtm-strategy, ideal-customer-profile, account-research, cold-email-writing]
---

# Positioning and messaging

Positioning is the context that makes a product's value clear to a specific
buyer. Messaging is how that context is expressed. Start with Neyvro's existing
onboarding answers, product documents, approved positioning, approved claims,
and evidence. Do not create a duplicate product database.

This skill works as a knowledge-only advisor when Neyvro is disconnected. In
connected mode it reads authorized product context and approved claims. Drafts
are reviewable; positioning, claims, brand voice, and external messages are not
changed without an authorized proposal and approval.

## 1. Build the product and category context

Collect and label:

- product name, category, buyer, user, and job to be done;
- documented capabilities and constraints;
- real competitor alternatives, including manual work, spreadsheets,
  in-house systems, delay, or doing nothing;
- customer problems in the customer's language;
- target industries, use cases, and buyer personas;
- approved brand voice and words to prefer or avoid;
- approved claims, proof points, sources, dates, and version;
- unknowns and claims requiring review.

Use a market category the buyer recognizes and can budget for. If category,
capability, or problem information is missing, say so. Do not fill gaps with
generic product marketing language and do not infer a capability from a product
name.

## 2. Positioning components

Work through these five components:

1. Competitive alternatives: what the buyer actually does without the product,
   and where each alternative wins.
2. Unique capabilities: documented capabilities that are meaningfully different
   from the alternatives.
3. Value: what the capability changes for the buyer, expressed as a problem or
   outcome rather than a feature.
4. Target persona: the buyer role that cares most about the value, plus users,
   champions, approvers, and blockers.
5. Category: the frame that helps the buyer understand what the product is.

A feature is not differentiation until it explains a meaningful advantage against
a real alternative. Be honest about where the alternative wins.

## 3. Before / after / bridge

Use this structure:

- Before: the customer's current painful state, supported by customer language or
  evidence.
- After: the better state the product can credibly enable; label the outcome as a
  hypothesis when proof is absent.
- Bridge: the product's documented capabilities, kept brief.

Lead with the buyer's outcome, not a feature list. Never turn an unapproved
capability into a promise.

## 4. Value proposition and message house

Return:

- a one-line value proposition: product category plus buyer-relevant outcome;
- three message pillars;
- one reason-to-believe or proof point under each pillar;
- the caveat or unsupported claim under each pillar;
- buyer-specific variants for the economic buyer, champion, user, approver, and
  blocker where context supports them;
- objection-aware reframes that acknowledge where alternatives may win.

A message house is not a license to manufacture proof. If a pillar has no
approved proof, mark it as a research gap and keep the language conditional.

## 5. Differentiation and battlecards

For each named alternative, create a compact battlecard:

| Field | Requirement |
|---|---|
| Alternative | confirmed competitor, manual process, or status quo |
| Buyer reason | why the buyer chooses it today |
| Neyvro difference | documented capability and relevant buyer value |
| Where the alternative wins | honest tradeoff |
| Proof | approved claim/source or explicit missing proof |
| Reframe | one respectful, non-defamatory response |
| Do not claim | unsupported weakness or superiority |

Never manufacture competitor weaknesses, customer results, testimonials, market
share, certifications, or product capabilities. If competitor information is
unverified, identify it as an information gap rather than a weakness.

## 6. Buyer-specific messaging

For each persona, map:

- role and buying influence;
- job and pain;
- desired outcome;
- message angle;
- evidence/proof;
- likely objection;
- honest response;
- next safe action.

Use the customer's approved brand voice. If no voice is approved, use clear,
specific, restrained language and mark voice as unconfirmed. Do not impersonate
a customer or claim that a persona said something they did not say.

## 7. Objection-aware messaging

Handle objections by acknowledging the buyer's current alternative first:

- “We already use a spreadsheet” → explain the documented gap the product closes;
- “Our team can build this” → compare maintenance, ownership, and evidence only
  when those facts are approved;
- “We do not need this yet” → state the trigger or cost hypothesis and ask for
  validation, not urgency theater;
- “We need proof/security review” → return approved proof or identify exactly
  what evidence is missing.

No objection response may introduce a new unsupported claim.

## 8. Versioning and approval

Every generated positioning artifact returns a version and approval status:

- draft: generated from supplied facts and not approved;
- needs_approval: contains unsupported claims, missing proof, unconfirmed voice,
  or changed positioning;
- approved: only when the connected source contains an approved version and
  every surfaced claim is within approved claims;
- blocked: a required authorized source or approval is unavailable.

Reading approved positioning is safe. Proposing changes is not persistence.
Customer-approved positioning and claims must remain unchanged until a customer
authorized proposal is approved by the existing Neyvro service.

## 9. Structured output

Return exactly these top-level fields:

- positioning_summary: category, one-liner, before/after/bridge, and version;
- target_persona: role, influence, evidence status, and buyer-specific context;
- problem_statement: problem, cost/impact hypothesis, and evidence;
- differentiation: documented capabilities, real alternatives, honest tradeoffs,
  and battlecards;
- proof_points: approved claims and sources only;
- message_angles: persona-specific, objection-aware draft angles;
- unsupported_claims: every capability, outcome, comparison, or proof that cannot
  be safely stated as fact;
- approval_status: draft, needs_approval, approved, or blocked.

Also include assumptions, research gaps, brand-voice status, and evidence IDs
inside the relevant objects. If product information is incomplete, return a
useful framework with explicit gaps instead of inventing content.

## 10. Neyvro MCP contracts

These are safe adapter contracts. The current repository does not expose these
endpoints, so connected functionality remains disabled until a real adapter is
injected.

### neyvro_get_product_context

Input: { "workspace_id": "uuid" }

Output: { "status": "available|disabled|blocked", "product_context": {}, "evidence": [], "research_gaps": [] }

Reads existing onboarding, product documents, and approved workspace context. It
must enforce tenant authorization and must not create a duplicate product record.

### neyvro_get_positioning

Input: { "workspace_id": "uuid", "version": "latest|uuid" }

Output: { "status": "available|disabled|blocked", "positioning": {}, "version": "string", "approval_status": "string", "evidence": [] }

Reads a versioned approved or draft positioning artifact without changing it.

### neyvro_propose_positioning

Input: { "workspace_id": "uuid", "positioning": {}, "evidence_ids": [], "idempotency_key": "uuid" }

Output: { "status": "proposed|disabled|blocked", "proposal_id": "uuid", "version": "string", "approval_required": true }

Creates a versioned review proposal only. It must not mutate approved
positioning, claims, brand voice, onboarding, CRM, or outbound messages.

### neyvro_get_approved_claims

Input: { "workspace_id": "uuid", "version": "latest|uuid" }

Output: { "status": "available|disabled|blocked", "claims": [], "version": "string", "evidence": [] }

Reads the allowlist of claims that may be stated as fact. No approved claim may
be silently edited or widened by this skill.

## Behavior modes and safety

- Knowledge-only: teach positioning and produce conditional drafts from supplied
  facts; no login or MCP is required.
- Research: read tenant-scoped product documents, positioning, claims, and
  evidence; return provenance and gaps.
- Draft-only: create a reviewable message house, battlecards, and persona
  variants; do not publish or send.
- External action: use only the proposal contract and require explicit approval,
  audit logging, provider scope, and idempotency.

Load related skills on demand: gtm-strategy for motion fit,
ideal-customer-profile for target accounts, account-research for evidence, and
cold-email-writing for channel-specific copy.
