"""Evidence-safe account research over an existing Neyvro company twin."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

CONTRACTS = ("neyvro_research_company", "neyvro_get_company_twin", "neyvro_get_company_signals", "neyvro_get_company_timeline", "neyvro_get_evidence")
TIER_BUDGETS = {"A": {"minutes": 15, "source_fetches": 12}, "B": {"minutes": 5, "source_fetches": 5}, "C": {"minutes": 1, "source_fetches": 1}}
FRESHNESS_DAYS = {"A": 7, "B": 14, "C": 30}


@dataclass(frozen=True)
class ResearchEvidence:
    evidence_id: str
    source: str
    statement: str
    observed_at: datetime
    category: str = "general"
    confidence: float = 1.0
    polarity: str = "supporting"


@dataclass(frozen=True)
class CompanyTwin:
    company_id: str
    name: str
    exists: bool = True
    authorized: bool = True
    industry: str | None = None
    approximate_size: str | None = None
    business_model: str | None = None
    technology_stack: tuple[str, ...] = ()
    relationship_history: tuple[str, ...] = ()
    buyers: tuple[str, ...] = ()
    evidence: tuple[ResearchEvidence, ...] = ()
    last_researched_at: datetime | None = None
    stale_fields: tuple[str, ...] = ()
    disqualifiers: tuple[str, ...] = ()


@dataclass(frozen=True)
class ResearchRequest:
    account_tier: str | None = None
    now: datetime | None = None
    used_fetches: int = 0
    include_relationship_history: bool = False


@dataclass(frozen=True)
class ResearchBrief:
    status: str
    account_tier: str
    why_this_company: str
    why_now: str
    relevant_buyers: tuple[str, ...]
    supporting_evidence: tuple[dict[str, Any], ...]
    negative_evidence: tuple[dict[str, Any], ...]
    verified_observations: tuple[dict[str, Any], ...]
    inferences: tuple[str, ...]
    predictions: tuple[str, ...]
    uncertainty: tuple[str, ...]
    unknown_facts: tuple[str, ...]
    disqualifiers: tuple[str, ...]
    recommended_next_action: str
    outreach_angle: dict[str, Any]
    research_budget: dict[str, int]
    freshness: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        result = self.__dict__.copy()
        for field in ("relevant_buyers", "supporting_evidence", "negative_evidence", "verified_observations", "inferences", "predictions", "uncertainty", "unknown_facts", "disqualifiers"):
            result[field] = list(result[field])
        return result


def _evidence_dict(item: ResearchEvidence) -> dict[str, Any]:
    return {"evidence_id": item.evidence_id, "source": item.source, "statement": item.statement, "observed_at": item.observed_at.isoformat(), "category": item.category, "confidence": item.confidence, "polarity": item.polarity}


def _fresh(item: ResearchEvidence, now: datetime, tier: str) -> bool:
    return item.observed_at >= now - timedelta(days=FRESHNESS_DAYS[tier])


def _empty_brief(status: str, twin: CompanyTwin, tier: str, budget: dict[str, int], action: str, unknowns: tuple[str, ...]) -> ResearchBrief:
    return ResearchBrief(status, tier, "", "", (), (), (), (), (), (), (), unknowns, twin.disqualifiers, action, {"status": "not_ready", "text": "", "evidence_ids": []}, {**budget, "used_fetches": 0}, {"last_researched_at": twin.last_researched_at.isoformat() if twin.last_researched_at else None, "stale_fields": []})


def research_company(twin: CompanyTwin, request: ResearchRequest = ResearchRequest()) -> ResearchBrief:
    """Build a bounded, cited brief without network access or persistence."""
    now = request.now or datetime.now(timezone.utc)
    tier = request.account_tier if request.account_tier in TIER_BUDGETS else "unknown"
    budget = TIER_BUDGETS.get(tier, TIER_BUDGETS["C"])
    if not twin.exists:
        return _empty_brief("not_found", twin, tier, budget, "Verify the company identifier or domain before researching.", ("company identity",))
    if not twin.authorized:
        return _empty_brief("unauthorized", twin, tier, budget, "Request tenant authorization before accessing this company.", ("authorized company access",))
    evidence = tuple(sorted(twin.evidence, key=lambda item: (item.observed_at, item.evidence_id), reverse=True))
    effective_tier = tier if tier != "unknown" else "C"
    fresh = tuple(item for item in evidence if _fresh(item, now, effective_tier))
    stale = tuple(item for item in evidence if item not in fresh)
    negative = tuple(item for item in evidence if item.polarity == "negative")
    supporting = tuple(item for item in fresh if item.polarity != "negative")
    observations = tuple(_evidence_dict(item) for item in fresh)
    categories = {item.category for item in fresh}
    unknowns = list(twin.stale_fields)
    field_values = {"business model": twin.business_model, "industry": twin.industry, "approximate size": twin.approximate_size, "technology stack": twin.technology_stack, "buyers": twin.buyers}
    for field, value in field_values.items():
        if field not in categories and not value:
            unknowns.append(field)
    if stale:
        unknowns.append("freshness: existing research is stale and should not be used as a current trigger")
    contradictory: list[str] = []
    by_category: dict[str, set[str]] = {}
    for item in fresh:
        by_category.setdefault(item.category, set()).add(item.statement.casefold())
    for category, statements in by_category.items():
        if len(statements) > 1:
            contradictory.append(f"contradictory fresh signals in {category}")
    uncertainty = list(contradictory)
    if stale:
        uncertainty.append("some sources exceed the tier freshness window")
    triggers = tuple(item for item in supporting if item.category in {"technology_change", "hiring", "leadership", "expansion", "funding", "product"})
    trigger = triggers[0] if triggers else None
    angle_ready = bool(trigger and supporting and (twin.business_model or twin.industry) and not contradictory)
    if angle_ready:
        angle = {"status": "ready", "text": f"Discuss how the observed {trigger.category.replace('_', ' ')} may affect {twin.business_model or twin.industry}; validate whether it is a current priority.", "evidence_ids": [trigger.evidence_id]}
        why_now = trigger.statement
        next_action = "Validate the trigger with the relevant buyer before drafting outreach."
    else:
        angle = {"status": "not_ready", "text": "No single outreach angle is sufficiently supported by fresh, non-contradictory evidence.", "evidence_ids": []}
        why_now = "No fresh, corroborated trigger is available."
        next_action = "Resolve the listed research gaps or refresh stale sources before outreach."
    status = "stale" if not fresh or (stale and not triggers) else "researched"
    if contradictory:
        status = "stale"
    inferences = tuple(f"The evidence may indicate a priority around {trigger.category.replace('_', ' ')}." for trigger in (triggers[:1] if triggers else ()))
    predictions = tuple(f"If the {trigger.category.replace('_', ' ')} persists, the company may review related solutions." for trigger in (triggers[:1] if triggers else ()))
    why_company = f"{twin.name} matches the available account context for {twin.industry or 'an unconfirmed industry'}; validate fit against the approved ICP."
    if twin.disqualifiers:
        why_company = "Account research is available, but explicit disqualifiers limit suitability for the requested motion."
    return ResearchBrief(status, tier, why_company, why_now, twin.buyers, tuple(_evidence_dict(item) for item in supporting), tuple(_evidence_dict(item) for item in negative), observations, inferences, predictions, tuple(dict.fromkeys(uncertainty)), tuple(dict.fromkeys(unknowns)), twin.disqualifiers, next_action, angle, {**budget, "used_fetches": request.used_fetches}, {"last_researched_at": twin.last_researched_at.isoformat() if twin.last_researched_at else None, "stale_fields": list(twin.stale_fields) + (["evidence"] if stale else [])})


def safe_contract(name: str, payload: dict[str, Any], transport: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None) -> dict[str, Any]:
    """Call an injected real adapter, otherwise fail closed without login or crawling."""
    if name not in CONTRACTS:
        raise ValueError(f"unknown account-research contract: {name}")
    if transport is None:
        return {"status": "disabled", "contract": name, "reason": "Neyvro company-research backend adapter is not configured", "data": None}
    return transport(name, payload)
