"""Evidence-backed BANT/MEDDIC/MEDDPICC qualification and discovery briefs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

CONTRACTS = ("neyvro_get_opportunity_qualification", "neyvro_generate_discovery_brief", "neyvro_get_buying_committee", "neyvro_get_meeting_context")
FRAMEWORKS = {"BANT", "MEDDIC", "MEDDPICC"}

FRAMEWORK_FIELDS = {
    "BANT": ("budget", "authority", "need", "timeline"),
    "MEDDIC": ("metrics", "economic_buyer", "decision_criteria", "decision_process", "pain", "champion"),
    "MEDDPICC": ("metrics", "economic_buyer", "decision_criteria", "decision_process", "pain", "champion", "paper_process", "competition"),
}


@dataclass(frozen=True)
class QualificationEvidence:
    evidence_id: str
    statement: str
    source: str
    dimension: str
    verified: bool = True
    observed_at: datetime | None = None
    subject: str = "opportunity"


@dataclass(frozen=True)
class OpportunityContext:
    opportunity_id: str
    tenant_id: str
    account_name: str
    account_id: str
    buyer_name: str | None = None
    buyer_role: str | None = None
    buyer_is_decision_maker: bool | None = None
    evidence: tuple[QualificationEvidence, ...] = ()
    crm_fields: tuple[tuple[str, str], ...] = ()
    meeting_history: tuple[QualificationEvidence, ...] = ()
    conversation_evidence: tuple[QualificationEvidence, ...] = ()
    stakeholder_roles: tuple[str, ...] = ()
    objections: tuple[str, ...] = ()
    disqualifiers: tuple[str, ...] = ()
    is_nonbuyer: bool = False
    crm_available: bool = True
    meeting_api_available: bool = True


@dataclass(frozen=True)
class QualificationBrief:
    opportunity_id: str
    framework: str
    status: str
    account_briefing: str
    confirmed_facts: tuple[dict[str, Any], ...]
    qualification_dimensions: dict[str, dict[str, Any]]
    qualification_gaps: tuple[str, ...]
    conflicting_information: tuple[str, ...]
    buying_committee: tuple[dict[str, Any], ...]
    pain_severity: dict[str, Any]
    relevant_objections: tuple[str, ...]
    recommended_discovery_questions: tuple[str, ...]
    suggested_next_step: str
    research_gaps: tuple[str, ...]
    approval_status: str = "read_only"
    send_allowed: bool = False

    def as_dict(self) -> dict[str, Any]:
        result = self.__dict__.copy()
        for field in ("confirmed_facts", "qualification_gaps", "conflicting_information", "buying_committee", "relevant_objections", "recommended_discovery_questions", "research_gaps"):
            result[field] = list(result[field])
        return result


def _dimension_facts(context: OpportunityContext) -> dict[str, list[QualificationEvidence]]:
    facts: dict[str, list[QualificationEvidence]] = {}
    for item in context.evidence + context.meeting_history + context.conversation_evidence:
        if item.verified:
            facts.setdefault(item.dimension, []).append(item)
    return facts


def _dimension_status(items: list[QualificationEvidence]) -> tuple[str, list[str], list[str]]:
    if not items:
        return "unknown", [], []
    statements = {item.statement.casefold() for item in items}
    if len(statements) > 1:
        return "conflicting", [item.evidence_id for item in items], sorted(statements)
    return "confirmed", [item.evidence_id for item in items], []


def _questions(missing: list[str], buyer_role: str | None) -> list[str]:
    owner = buyer_role or "the team"
    questions = {
        "budget": "How is funding for this type of initiative normally approved, and what would need to be true to create or allocate it?",
        "authority": "Who else needs to be involved before a decision can be made?",
        "need": "What is happening today that makes this problem worth changing?",
        "timeline": "Is there a customer-defined event or planning window that affects timing?",
        "metrics": "What measurable outcome would make this initiative worthwhile?",
        "economic_buyer": "Who owns the business outcome and can approve the investment?",
        "decision_criteria": "What criteria will the buying group use to compare options?",
        "decision_process": "Could you walk me through the steps from evaluation to approval?",
        "pain": f"For {owner}, what is the operational impact of the problem today?",
        "champion": "Who would benefit most from solving this and help the team navigate the decision?",
        "paper_process": "What legal, security, procurement, or contracting steps are required?",
        "competition": "What alternatives, internal projects, or existing tools are being considered?",
    }
    return [questions[item] for item in missing if item in questions]


def qualify_opportunity(context: OpportunityContext, framework: str = "BANT") -> QualificationBrief:
    """Build a read-only qualification brief; unknown is never a positive score."""
    if framework not in FRAMEWORKS:
        raise ValueError(f"unknown qualification framework: {framework}")
    facts = _dimension_facts(context)
    dimensions: dict[str, dict[str, Any]] = {}
    gaps: list[str] = []
    conflicts: list[str] = []
    confirmed: list[dict[str, Any]] = []
    for dimension in FRAMEWORK_FIELDS[framework]:
        status, evidence_ids, statements = _dimension_status(facts.get(dimension, []))
        dimensions[dimension] = {"status": status, "evidence_ids": evidence_ids}
        if status == "confirmed":
            confirmed.extend({"dimension": dimension, "statement": item.statement, "source": item.source, "evidence_id": item.evidence_id} for item in facts[dimension])
        elif status == "conflicting":
            conflicts.append(f"{dimension}: {', '.join(statements)}")
            gaps.append(f"resolve conflicting {dimension} information")
        else:
            gaps.append(dimension)
    represented = {item["evidence_id"] for item in confirmed}
    for dimension, items in facts.items():
        for item in items:
            if item.evidence_id not in represented:
                confirmed.append({"dimension": dimension, "statement": item.statement, "source": item.source, "evidence_id": item.evidence_id})
    if context.is_nonbuyer or (context.buyer_is_decision_maker is False and not context.stakeholder_roles):
        gaps.append("verified path to an economic buyer or champion")
    disqualifiers = list(context.disqualifiers)
    for item in context.evidence:
        if item.verified and item.dimension == "disqualifier":
            disqualifiers.append(item.statement)
    if disqualifiers:
        status = "disqualified"
    elif context.is_nonbuyer and not context.stakeholder_roles:
        status = "nonbuyer"
    elif conflicts:
        status = "needs_review"
    elif gaps:
        status = "incomplete"
    else:
        status = "qualified"
    pain_items = facts.get("pain", [])
    pain_status, pain_ids, _ = _dimension_status(pain_items)
    pain = {"status": "confirmed" if pain_status == "confirmed" else "hypothesis" if pain_status == "unknown" and context.opportunity_id else pain_status, "evidence_ids": pain_ids, "severity": "unknown"}
    if pain_status == "confirmed":
        severity = "high" if any(word in item.statement.casefold() for item in pain_items for word in ("critical", "blocked", "lost", "urgent", "material")) else "unquantified"
        pain["severity"] = severity
    committee = tuple({"role": role, "status": "hypothesis", "evidence_ids": []} for role in context.stakeholder_roles)
    if context.buyer_name and context.buyer_role:
        committee = ({"name": context.buyer_name, "role": context.buyer_role, "status": "identified", "evidence_ids": [item.evidence_id for item in context.evidence if item.dimension in {"authority", "economic_buyer", "buyer"}]},) + committee
    research_gaps: list[str] = []
    if not context.crm_available:
        research_gaps.append("CRM opportunity API unavailable; stage and ownership not refreshed")
    if not context.meeting_api_available:
        research_gaps.append("meeting history API unavailable; prior commitments not verified")
    if not context.conversation_evidence:
        research_gaps.append("conversation intelligence unavailable or no conversation evidence supplied")
    next_step = "Resolve the highest-value qualification gap in a discovery conversation." if status in {"incomplete", "needs_review", "nonbuyer"} else "Confirm the documented decision process and next customer-owned commitment." if status == "qualified" else "Exit or place in an authorized nurture path; do not continue active qualification."
    briefing = f"{context.account_name} opportunity {context.opportunity_id}: {len(confirmed)} qualification fact(s) confirmed under {framework}; budget and timing are never inferred."
    return QualificationBrief(context.opportunity_id, framework, status, briefing, tuple(confirmed), dimensions, tuple(dict.fromkeys(gaps)), tuple(conflicts), committee, pain, context.objections, tuple(_questions(gaps, context.buyer_role)), next_step, tuple(dict.fromkeys(research_gaps)), "read_only", False)


def safe_contract(name: str, payload: dict[str, Any], transport: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None) -> dict[str, Any]:
    """Call an injected CRM/meeting adapter, otherwise preserve read-only planning."""
    if name not in CONTRACTS:
        raise ValueError(f"unknown qualification contract: {name}")
    if transport is None:
        return {"status": "disabled", "contract": name, "reason": "Neyvro CRM/meeting qualification adapter is not configured", "data": None, "send_allowed": False}
    result = transport(name, payload)
    result["send_allowed"] = False
    return result
