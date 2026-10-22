"""Read-only, evidence-bounded primitives for Neyvro company intelligence skills."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Iterable

CONTRACTS = (
    "neyvro_get_company_twin", "neyvro_get_company_timeline", "neyvro_get_company_signals", "neyvro_get_evidence",
    "neyvro_get_predictive_opportunities", "neyvro_evaluate_icp_fit", "neyvro_get_buying_windows", "neyvro_search_buyers",
    "neyvro_get_opportunity_buyers", "neyvro_get_buying_committee", "neyvro_get_investigation_status", "neyvro_research_company",
    "neyvro_get_negative_evidence", "neyvro_get_revenue_attribution", "neyvro_get_pipeline_metrics", "neyvro_get_campaign_metrics",
)


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    tenant_id: str
    claim: str
    classification: str = "observed_fact"
    source: str = "unknown"
    observed_at: datetime | None = None
    freshness_days: int | None = None
    confidence: float | None = None


@dataclass(frozen=True)
class CompanyTwin:
    tenant_id: str
    company_id: str
    authorized: bool = True
    current_state: dict[str, Any] | None = None
    history: tuple[dict[str, Any], ...] = ()
    transitions: tuple[dict[str, Any], ...] = ()
    evidence: tuple[EvidenceRecord, ...] = ()


def _evidence_dict(item: EvidenceRecord, *, stale_after_days: int = 180) -> dict[str, Any]:
    stale = item.freshness_days is not None and item.freshness_days > stale_after_days
    classification = "stale" if stale else item.classification
    return {"evidence_id": item.evidence_id, "tenant_id": item.tenant_id, "claim": item.claim, "classification": classification, "source": item.source, "observed_at": item.observed_at.isoformat() if item.observed_at else None, "freshness_days": item.freshness_days, "confidence": item.confidence, "stale": stale}


def _in_scope(evidence: Iterable[EvidenceRecord], tenant_id: str) -> list[EvidenceRecord]:
    return [item for item in evidence if item.tenant_id == tenant_id]


def verify_evidence(evidence: tuple[EvidenceRecord, ...], tenant_id: str, *, stale_after_days: int = 180) -> dict[str, Any]:
    scoped = _in_scope(evidence, tenant_id)
    records = [_evidence_dict(item, stale_after_days=stale_after_days) for item in scoped]
    by_claim: dict[str, list[dict[str, Any]]] = {}
    for item in records:
        by_claim.setdefault(item["claim"].casefold(), []).append(item)
    contradictions = [items for items in by_claim.values() if any(item["classification"] == "contradictory" for item in items)]
    verified = [item for item in records if item["classification"] == "observed_fact" and not item["stale"]]
    inferred = [item for item in records if item["classification"] in {"reasonable_inference", "prediction"}]
    stale = [item for item in records if item["stale"]]
    return {"status": "partial" if stale or contradictions else "available", "verified_claims": verified, "inferred_claims": inferred, "stale_evidence": stale, "contradictions": contradictions, "unsupported_claims": [], "missing_data": [] if records else ["authorized evidence records"], "tenant_scope": tenant_id}


def analyze_company_twin(twin: CompanyTwin, *, stale_after_days: int = 180) -> dict[str, Any]:
    if not twin.authorized:
        return {"status": "blocked", "company_id": twin.company_id, "current_state": None, "historical_timeline": [], "transitions": [], "supporting_evidence": [], "unknowns": ["company authorization"], "contradictions": []}
    verified = verify_evidence(twin.evidence, twin.tenant_id, stale_after_days=stale_after_days)
    unknowns = []
    if twin.current_state is None:
        unknowns.append("current company state")
    if not twin.history:
        unknowns.append("company history")
    if not twin.transitions:
        unknowns.append("company transitions")
    return {"status": "partial" if unknowns or verified["status"] != "available" else "available", "company_id": twin.company_id, "current_state": twin.current_state, "historical_timeline": list(twin.history), "transitions": list(twin.transitions), "supporting_evidence": verified["verified_claims"], "inferences": verified["inferred_claims"], "unknowns": unknowns + verified["missing_data"], "contradictions": verified["contradictions"]}


def detect_technology_changes(changes: tuple[dict[str, Any], ...], evidence: tuple[EvidenceRecord, ...], tenant_id: str) -> dict[str, Any]:
    verified = verify_evidence(evidence, tenant_id)
    allowed_ids = {item["evidence_id"] for item in verified["verified_claims"]}
    observed = [change for change in changes if set(change.get("evidence_ids", ())) & allowed_ids]
    return {"status": "partial" if not observed or verified["status"] != "available" else "available", "changes": observed, "technology_gaps": [change for change in observed if change.get("gap")], "observed_facts": [change for change in observed if change.get("kind") in {"adoption", "migration", "engineering", "security", "cloud"}], "inferences": [], "unknowns": ["desired infrastructure state"] if not any(change.get("desired_state") for change in observed) else [], "contradictions": verified["contradictions"]}


def predict_problem_intelligence(changes: tuple[dict[str, Any], ...], icp: dict[str, Any] | None, evidence: tuple[EvidenceRecord, ...], tenant_id: str) -> dict[str, Any]:
    verified = verify_evidence(evidence, tenant_id)
    ids = {item["evidence_id"] for item in verified["verified_claims"]}
    hypotheses = []
    for change in changes:
        supporting = sorted(set(change.get("evidence_ids", ())) & ids)
        if supporting:
            hypotheses.append({"hypothesis": change.get("possible_problem", "possible customer-relevant problem requires validation"), "trigger": change.get("kind", "unknown"), "evidence_ids": supporting, "icp_relevance": change.get("icp_relevance", "unknown"), "confidence": "not_asserted", "validation_question": change.get("validation_question", "Is this a current priority?")})
    return {"status": "partial" if not hypotheses else "available", "problem_hypotheses": hypotheses, "supporting_evidence": sorted(ids), "counter_evidence": [], "validation_questions": [item["validation_question"] for item in hypotheses], "unknowns": [] if hypotheses else ["verified trigger evidence"], "disqualifiers": list((icp or {}).get("exclusions", ())) }


def detect_buying_window(signals: tuple[dict[str, Any], ...], evidence: tuple[EvidenceRecord, ...], tenant_id: str) -> dict[str, Any]:
    verified = verify_evidence(evidence, tenant_id)
    ids = {item["evidence_id"] for item in verified["verified_claims"]}
    reasons = [signal for signal in signals if set(signal.get("evidence_ids", ())) & ids]
    return {"status": "partial" if len(reasons) < 2 or verified["status"] != "available" else "available", "window_reasons": reasons, "timing_evidence": sorted({eid for signal in reasons for eid in signal.get("evidence_ids", ()) if eid in ids}), "counter_evidence": [], "recommended_expiry": None, "validation_questions": ["What timing or initiative would make this relevant now?"], "uncertainty": "A signal does not prove buying intent, budget, or urgency."}


def match_buyer_opportunity(problem: str, buyers: tuple[dict[str, Any], ...], evidence: tuple[EvidenceRecord, ...], tenant_id: str) -> dict[str, Any]:
    verified = verify_evidence(evidence, tenant_id)
    ids = {item["evidence_id"] for item in verified["verified_claims"]}
    matches = [buyer for buyer in buyers if set(buyer.get("evidence_ids", ())) & ids and buyer.get("responsibility")]
    return {"status": "available" if matches else "partial", "problem": problem, "matches": matches, "missing_stakeholders": [] if matches else ["authorized buyer responsibility evidence"], "unknowns": [] if matches else ["buyer role and responsibility"], "tenant_scope": tenant_id}


def plan_continuous_investigation(unresolved: tuple[dict[str, Any], ...], allowed_actions: tuple[dict[str, Any], ...], *, budget_remaining: int, fresh: bool = True) -> dict[str, Any]:
    permitted = [action for action in allowed_actions if action.get("cost", 0) <= budget_remaining and action.get("authorized", False)]
    blocked = [action for action in allowed_actions if action not in permitted]
    if fresh:
        blocked += [{"reason": "existing verified research is fresh; avoid repeated crawl"}]
    return {"status": "available" if permitted else "partial", "unresolved_questions": list(unresolved), "allowed_actions": permitted, "blocked_actions": blocked, "budget_remaining": budget_remaining, "stopping_conditions": ["budget exhausted", "question resolved", "evidence remains unavailable"]}


def analyze_negative_evidence(facts: tuple[dict[str, Any], ...], evidence: tuple[EvidenceRecord, ...], tenant_id: str) -> dict[str, Any]:
    verified = verify_evidence(evidence, tenant_id)
    ids = {item["evidence_id"] for item in verified["verified_claims"]}
    findings = [fact for fact in facts if set(fact.get("evidence_ids", ())) & ids]
    return {"status": "available" if findings else "partial", "observed_negative": [item for item in findings if item.get("kind") == "negative"], "missing_prerequisite": [item for item in findings if item.get("kind") == "missing_prerequisite"], "contradictions": verified["contradictions"], "disqualifiers": [item for item in findings if item.get("disqualifier") is True], "not_observed": [item for item in facts if item not in findings], "tenant_scope": tenant_id}


def attribute_revenue(events: tuple[dict[str, Any], ...], tenant_id: str, *, model: str = "customer_declared") -> dict[str, Any]:
    scoped = [event for event in events if event.get("tenant_id") == tenant_id]
    missing = [event for event in scoped if not event.get("opportunity_id") or event.get("value") is None]
    attributed = sum(float(event["value"]) for event in scoped if event.get("value") is not None and event.get("opportunity_id"))
    return {"status": "partial" if missing or not scoped else "available", "model": model, "attributed_revenue": attributed if scoped else None, "touchpoints": scoped, "unattributed_events": missing, "missing_links": ["CRM opportunity join"] if missing else [], "data_quality": {"tenant_filtered": True, "event_count": len(scoped)}, "causal_limits": ["Attribution is not causal impact without a valid causal design."]}


def safe_contract(name: str, payload: dict[str, Any], transport: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None) -> dict[str, Any]:
    if name not in CONTRACTS:
        raise ValueError(f"unknown intelligence contract: {name}")
    if transport is None:
        return {"status": "disabled", "contract": name, "reason": "Neyvro intelligence adapter is not configured", "data": None}
    return transport(name, payload)
