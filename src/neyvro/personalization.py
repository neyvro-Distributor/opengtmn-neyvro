"""Evidence-linked personalization snippets with explicit confidence limits."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

CONTRACTS = ("neyvro_get_personalization_context", "neyvro_generate_personalization", "neyvro_validate_outreach_claims", "neyvro_get_brand_voice")
EFFORT_LEVELS = {"high_touch_strategic", "medium_touch_qualified", "lightweight_relevant"}
CATEGORIES = {"verified_trigger", "why_now", "relevant_pain_hypothesis", "product_benefit", "proof_point", "call_to_action"}
HYPE_WORDS = {"guaranteed", "revolutionary", "amazing", "instant", "best-in-class", "10x"}


@dataclass(frozen=True)
class PersonalizationEvidence:
    evidence_id: str
    statement: str
    source: str
    observed_at: datetime | None = None
    verified: bool = True
    category: str = "general"
    relevant_roles: tuple[str, ...] = ()


@dataclass(frozen=True)
class MessageMaterial:
    text: str
    evidence_ids: tuple[str, ...] = ()
    generic: bool = False
    approved: bool = True
    source: str | None = None


@dataclass(frozen=True)
class PersonalizationContext:
    company_id: str
    company_name: str
    buyer_id: str
    buyer_role: str
    buyer_responsibilities: tuple[str, ...] = ()
    opportunity_hypothesis: str | None = None
    signals: tuple[PersonalizationEvidence, ...] = ()
    relationship_history: tuple[PersonalizationEvidence, ...] = ()
    product_benefit: MessageMaterial = MessageMaterial("")
    proof_point: MessageMaterial = MessageMaterial("")
    call_to_action: MessageMaterial = MessageMaterial("Would it be useful to compare notes?")
    brand_voice: str | None = None
    brand_voice_version: str | None = None
    positioning_version: str | None = None


@dataclass(frozen=True)
class PersonalizationAssessment:
    effort_level: str
    snippets: tuple[dict[str, Any], ...]
    confidence_limitations: tuple[str, ...]
    evidence_links: tuple[dict[str, Any], ...]
    flagged_claims: tuple[dict[str, Any], ...]
    brand_voice: dict[str, Any]
    approval_status: str
    send_allowed: bool = False

    def as_dict(self) -> dict[str, Any]:
        result = self.__dict__.copy()
        for field in ("snippets", "confidence_limitations", "evidence_links", "flagged_claims"):
            result[field] = list(result[field])
        return result


def _role_match(item: PersonalizationEvidence, role: str) -> bool:
    return not item.relevant_roles or role.casefold() in {value.casefold() for value in item.relevant_roles}


def validate_outreach_claims(context: PersonalizationContext, snippets: tuple[dict[str, Any], ...], effort_level: str) -> dict[str, Any]:
    evidence = {item.evidence_id: item for item in context.signals + context.relationship_history}
    approved_material_ids = set(context.product_benefit.evidence_ids) | set(context.proof_point.evidence_ids)
    flags: list[dict[str, Any]] = []
    links: list[str] = []
    statements_by_category: dict[str, set[str]] = {}
    for snippet in snippets:
        category = snippet.get("category")
        text = snippet.get("text", "")
        if category not in CATEGORIES:
            flags.append({"claim": text, "reason": "unknown_snippet_category", "evidence_ids": []})
        ids = tuple(snippet.get("evidence_ids", ()))
        links.extend(ids)
        if not snippet.get("generic", False) and category not in {"product_benefit", "call_to_action"} and not ids:
            flags.append({"claim": text, "reason": "missing_evidence", "evidence_ids": []})
        for evidence_id in ids:
            if category in {"product_benefit", "proof_point"} and evidence_id in approved_material_ids:
                continue
            item = evidence.get(evidence_id)
            if item is None:
                flags.append({"claim": text, "reason": "evidence_mismatch", "evidence_ids": [evidence_id]})
                continue
            if not item.verified:
                flags.append({"claim": text, "reason": "unverified_evidence", "evidence_ids": [evidence_id]})
            if not _role_match(item, context.buyer_role):
                flags.append({"claim": text, "reason": "buyer_role_mismatch", "evidence_ids": [evidence_id]})
            statements_by_category.setdefault(item.category, set()).add(item.statement.casefold())
        if any(word in text.casefold() for word in HYPE_WORDS):
            flags.append({"claim": text, "reason": "unsupported_guarantee_or_hype", "evidence_ids": list(ids)})
    for category, statements in statements_by_category.items():
        if len(statements) > 1:
            flags.append({"claim": category, "reason": "contradictory_signals", "evidence_ids": [item.evidence_id for item in context.signals if item.category == category]})
    if effort_level == "high_touch_strategic" and not any(item.get("category") == "verified_trigger" and item.get("evidence_ids") for item in snippets):
        flags.append({"claim": "high-touch strategic personalization", "reason": "verified_trigger_required", "evidence_ids": []})
    voice_text = context.brand_voice or "unknown"
    if any(word in " ".join(item.get("text", "") for item in snippets).casefold() for word in HYPE_WORDS):
        voice_status = "flagged"
    else:
        voice_status = "consistent" if context.brand_voice else "unknown"
    return {"status": "blocked" if flags and any(item["reason"] in {"evidence_mismatch", "buyer_role_mismatch", "contradictory_signals"} for item in flags) else "flagged" if flags else "valid", "flagged_claims": flags, "evidence_ids": list(dict.fromkeys(links)), "brand_voice": {"status": voice_status, "applied": voice_text, "version": context.brand_voice_version}}


def generate_personalization(context: PersonalizationContext, effort_level: str = "medium_touch_qualified") -> PersonalizationAssessment:
    """Generate reusable snippets from supplied context only; never send."""
    if effort_level not in EFFORT_LEVELS:
        raise ValueError(f"unknown effort level: {effort_level}")
    verified = tuple(item for item in context.signals if item.verified)
    triggers = tuple(item for item in verified if item.category in {"trigger", "hiring", "funding", "migration", "launch", "expansion"})
    contradictions = {item.category for item in verified if sum(other.category == item.category for other in verified) > 1 and len({other.statement.casefold() for other in verified if other.category == item.category}) > 1}
    selected = triggers[0] if triggers else (verified[0] if verified else None)
    snippets: list[dict[str, Any]] = []
    limitations: list[str] = []
    pre_flags: list[dict[str, Any]] = []
    if selected and selected.category in contradictions:
        pre_flags.append({"claim": selected.statement, "reason": "contradictory_signals", "evidence_ids": [item.evidence_id for item in verified if item.category == selected.category]})
    if selected and not _role_match(selected, context.buyer_role):
        pre_flags.append({"claim": selected.statement, "reason": "buyer_role_mismatch", "evidence_ids": [selected.evidence_id]})
    if selected and selected.category not in contradictions and _role_match(selected, context.buyer_role):
        snippets.append({"category": "verified_trigger", "text": selected.statement, "evidence_ids": [selected.evidence_id], "generic": False, "confidence": 0.9})
        snippets.append({"category": "why_now", "text": f"That may make {context.buyer_role}'s priorities around this topic timely; validate before asserting it.", "evidence_ids": [selected.evidence_id], "generic": False, "confidence": 0.6})
        snippets.append({"category": "relevant_pain_hypothesis", "text": f"Could this be creating additional work for {context.buyer_role}?", "evidence_ids": [selected.evidence_id], "generic": False, "confidence": 0.5})
    else:
        limitations.append("No non-contradictory, buyer-role-matched verified trigger is available.")
    if effort_level == "high_touch_strategic" and not selected:
        limitations.append("High-touch output requires a verified trigger and is not ready.")
    benefit = context.product_benefit
    snippets.append({"category": "product_benefit", "text": benefit.text or "Approved product benefit is unavailable; use generic product context only.", "evidence_ids": list(benefit.evidence_ids), "generic": benefit.generic or not benefit.evidence_ids, "confidence": 0.8 if benefit.approved else 0.3})
    proof = context.proof_point
    if effort_level != "lightweight_relevant" and proof.text:
        snippets.append({"category": "proof_point", "text": proof.text, "evidence_ids": list(proof.evidence_ids), "generic": proof.generic, "confidence": 0.8 if proof.approved else 0.3})
    cta = context.call_to_action
    snippets.append({"category": "call_to_action", "text": cta.text, "evidence_ids": list(cta.evidence_ids), "generic": True, "confidence": 0.8})
    check = validate_outreach_claims(context, tuple(snippets), effort_level)
    flags = tuple(pre_flags + check["flagged_claims"])
    if effort_level == "lightweight_relevant" and not selected:
        limitations.append("Output is generic product messaging, not individualized account personalization.")
    status = "blocked" if check["status"] == "blocked" else "needs_evidence" if flags or limitations and effort_level == "high_touch_strategic" else "draft_ready"
    links = tuple(item for item in context.signals + context.relationship_history if item.evidence_id in check["evidence_ids"])
    evidence_links = tuple({"evidence_id": item.evidence_id, "source": item.source, "observed_at": item.observed_at.isoformat() if item.observed_at else None} for item in links)
    return PersonalizationAssessment(effort_level, tuple(snippets), tuple(dict.fromkeys(limitations)), evidence_links, flags, check["brand_voice"], status, False)


def safe_contract(name: str, payload: dict[str, Any], transport: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None) -> dict[str, Any]:
    """Use an injected Neyvro adapter only; otherwise fail closed."""
    if name not in CONTRACTS:
        raise ValueError(f"unknown personalization contract: {name}")
    if transport is None:
        return {"status": "disabled", "contract": name, "reason": "Neyvro personalization adapter is not configured", "data": None, "send_allowed": False}
    result = transport(name, payload)
    result["send_allowed"] = False
    return result
