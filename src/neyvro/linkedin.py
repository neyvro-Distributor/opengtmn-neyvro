"""Authorized LinkedIn context and manual-outreach assistance only."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

CONTRACTS = ("neyvro_get_linkedin_prospect_context", "neyvro_draft_linkedin_message", "neyvro_get_social_relationship", "neyvro_record_manual_outreach")
UNSUPPORTED_ACTIONS = {"send_connection_request", "send_dm", "automated_dm", "automated_comment", "scrape", "browser_automation", "bulk_connect"}


@dataclass(frozen=True)
class LinkedInEvidence:
    evidence_id: str
    statement: str
    source: str
    verified: bool = True
    observed_at: datetime | None = None
    professional: bool = True


@dataclass(frozen=True)
class ProspectProfile:
    prospect_id: str
    tenant_id: str
    company_id: str
    name: str
    company: str
    current_role: str | None = None
    profile_url: str | None = None
    role_verified_at: datetime | None = None
    authorized: bool = True
    evidence: tuple[LinkedInEvidence, ...] = ()


@dataclass(frozen=True)
class Relationship:
    tenant_id: str
    prospect_id: str
    state: str = "unknown"
    last_interaction_at: datetime | None = None
    opted_out: bool = False
    source: str | None = None


@dataclass(frozen=True)
class LinkedInDraft:
    status: str
    prospect_id: str
    action: str
    message: str
    engagement_suggestion: str | None
    angle: str
    evidence_ids: tuple[str, ...]
    flagged_claims: tuple[dict[str, Any], ...]
    relationship_state: str
    approval_status: str
    manual_steps: tuple[str, ...]
    external_action_executed: bool = False

    def as_dict(self) -> dict[str, Any]:
        result = self.__dict__.copy()
        result["evidence_ids"] = list(self.evidence_ids)
        result["flagged_claims"] = list(self.flagged_claims)
        result["manual_steps"] = list(self.manual_steps)
        return result


def get_prospect_context(profile: ProspectProfile | None, tenant_id: str, now: datetime | None = None, freshness_days: int = 30) -> dict[str, Any]:
    """Return non-disclosing, freshness-aware context for one authorized tenant."""
    now = now or datetime.now(timezone.utc)
    if profile is None or profile.tenant_id != tenant_id:
        return {"status": "not_found", "prospect_id": None, "context": None, "research_gaps": ["authorized professional profile"]}
    if not profile.authorized:
        return {"status": "blocked", "prospect_id": profile.prospect_id, "context": None, "research_gaps": ["provider authorization"]}
    if not profile.current_role or not profile.profile_url:
        return {"status": "missing_profile", "prospect_id": profile.prospect_id, "context": None, "research_gaps": ["profile URL and current role"]}
    if not profile.role_verified_at or profile.role_verified_at < now - timedelta(days=freshness_days):
        return {"status": "stale", "prospect_id": profile.prospect_id, "context": {"name": profile.name, "company": profile.company, "current_role": profile.current_role}, "research_gaps": ["fresh current-role verification"]}
    return {"status": "available", "prospect_id": profile.prospect_id, "context": {"name": profile.name, "company": profile.company, "current_role": profile.current_role, "profile_url": profile.profile_url, "evidence_ids": [item.evidence_id for item in profile.evidence if item.verified and item.professional]}, "research_gaps": []}


def draft_linkedin_message(profile: ProspectProfile | None, tenant_id: str, action: str = "connection_note", relationship: Relationship | None = None, now: datetime | None = None, freshness_days: int = 30) -> LinkedInDraft:
    """Draft an assisted action; never sends, publishes, or automates LinkedIn."""
    now = now or datetime.now(timezone.utc)
    relationship_state = relationship.state if relationship and relationship.tenant_id == tenant_id else "unknown"
    if action in UNSUPPORTED_ACTIONS:
        return LinkedInDraft("unsupported", profile.prospect_id if profile else "", action, "", None, "", (), ({"claim": action, "reason": "platform_action_not_supported"},), relationship_state, "unsupported", ("Use an officially authorized platform capability if later available.",), False)
    context = get_prospect_context(profile, tenant_id, now, freshness_days)
    if context["status"] != "available":
        return LinkedInDraft(context["status"], profile.prospect_id if profile else "", action, "", None, "", (), tuple({"claim": gap, "reason": "research_gap"} for gap in context["research_gaps"]), relationship_state, "blocked", ("Resolve the profile or authorization gap.",), False)
    verified = [item for item in profile.evidence if item.verified and item.professional]
    selected = verified[0] if verified else None
    if not selected:
        return LinkedInDraft("needs_evidence", profile.prospect_id, action, "", None, "", (), ({"claim": "professional context", "reason": "verified_evidence_missing"},), relationship_state, "review_required", ("Obtain permitted professional evidence.",), False)
    if relationship and relationship.opted_out:
        return LinkedInDraft("blocked", profile.prospect_id, action, "", None, "", (), ({"claim": "recipient", "reason": "relationship_opted_out"},), relationship_state, "blocked", ("Do not contact; honor opt-out.",), False)
    angle = selected.statement
    if action == "connection_note":
        message = f"Hi {profile.name.split()[0]} — I appreciated the perspective on {selected.statement.lower()}. I’d be glad to follow your work here."
        message = message[:300]
        engagement = None
    elif action == "direct_message":
        if relationship_state != "connected":
            return LinkedInDraft("blocked", profile.prospect_id, action, "", None, angle, (selected.evidence_id,), ({"claim": "relationship", "reason": "direct_message_requires_connected_relationship"},), relationship_state, "blocked", ("Customer must establish the relationship manually first.",), False)
        message = f"Hi {profile.name.split()[0]} — your work on {selected.statement.lower()} caught my attention. Would comparing notes be useful?"
        engagement = None
    else:
        message = ""
        engagement = f"Add a genuine, specific comment on the professional point: {selected.statement}"
    return LinkedInDraft("draft_ready", profile.prospect_id, action, message, engagement, angle, (selected.evidence_id,), (), relationship_state, "review_required", ("Review draft", "Open profile", "Customer acts manually", "Record confirmed action"), False)


def record_manual_outreach(tenant_id: str, profile: ProspectProfile | None, relationship: Relationship | None, action: str, confirmed_by_customer: bool, confirmed_at: datetime | None = None) -> dict[str, Any]:
    """Record only a customer-confirmed manual action, with tenant isolation."""
    if profile is None or profile.tenant_id != tenant_id or relationship and relationship.tenant_id != tenant_id:
        return {"status": "not_found", "recorded": False, "reason": "prospect is not available to this tenant"}
    if not confirmed_by_customer:
        return {"status": "blocked", "recorded": False, "reason": "customer confirmation is required"}
    return {"status": "recorded", "recorded": True, "prospect_id": profile.prospect_id, "action": action, "confirmed_at": (confirmed_at or datetime.now(timezone.utc)).isoformat(), "external_action_executed": False}


def safe_contract(name: str, payload: dict[str, Any], transport: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None) -> dict[str, Any]:
    """Call an injected authorized adapter, otherwise fail closed."""
    if name not in CONTRACTS:
        raise ValueError(f"unknown LinkedIn contract: {name}")
    if transport is None:
        return {"status": "disabled", "contract": name, "reason": "Neyvro LinkedIn adapter is not configured", "data": None, "external_action_executed": False}
    result = transport(name, payload)
    result["external_action_executed"] = False
    return result
