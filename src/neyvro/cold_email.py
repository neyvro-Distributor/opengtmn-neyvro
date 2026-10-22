"""Evidence-grounded, draft-only outbound email generation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

CONTRACTS = ("neyvro_draft_email", "neyvro_check_message_claims", "neyvro_get_email_draft")
FRAMEWORKS = {"PAS", "BAB", "AIDA", "trigger-first"}


@dataclass(frozen=True)
class MessageEvidence:
    evidence_id: str
    statement: str
    source: str
    verified: bool = True
    observed_at: datetime | None = None
    about_prospect: bool = True


@dataclass(frozen=True)
class EmailDraftRequest:
    opportunity_id: str
    buyer_id: str
    customer_product: str
    approved_positioning: str
    channel: str
    tone: str
    company_name: str | None = None
    buyer_name: str | None = None
    buyer_role: str | None = None
    framework: str = "trigger-first"
    prospect_evidence: tuple[MessageEvidence, ...] = ()
    positioning_evidence_ids: tuple[str, ...] = ()
    suppressed: bool = False
    opted_out: bool = False
    existing_customer: bool = False
    follow_up_count: int = 0


@dataclass(frozen=True)
class ClaimCheck:
    approval_status: str
    flagged_claims: tuple[dict[str, Any], ...]
    evidence_ids: tuple[str, ...]
    suppressed: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {"approval_status": self.approval_status, "flagged_claims": list(self.flagged_claims), "evidence_ids": list(self.evidence_ids), "suppressed": self.suppressed}


@dataclass(frozen=True)
class EmailDraft:
    opportunity_id: str
    buyer_id: str
    framework: str
    subject: str
    personalized_opener: dict[str, Any]
    problem_hypothesis: dict[str, Any]
    value_proposition: dict[str, Any]
    body: str
    call_to_action: str
    follow_up_variants: tuple[dict[str, Any], ...]
    evidence_ids: tuple[str, ...]
    flagged_claims: tuple[dict[str, Any], ...]
    approval_status: str
    send_allowed: bool = False

    def as_dict(self) -> dict[str, Any]:
        result = self.__dict__.copy()
        result["follow_up_variants"] = list(self.follow_up_variants)
        result["evidence_ids"] = list(self.evidence_ids)
        result["flagged_claims"] = list(self.flagged_claims)
        return result


def check_message_claims(claims: tuple[MessageEvidence, ...], evidence: tuple[MessageEvidence, ...] = (), *, suppressed: bool = False, opted_out: bool = False, existing_customer: bool = False, now: datetime | None = None, freshness_days: int = 30) -> ClaimCheck:
    """Validate claims without sending or persisting anything."""
    now = now or datetime.now(timezone.utc)
    evidence_by_id = {item.evidence_id: item for item in evidence}
    flags: list[dict[str, Any]] = []
    ids: list[str] = []
    for claim in claims:
        ids.append(claim.evidence_id)
        linked = evidence_by_id.get(claim.evidence_id, claim)
        if not claim.evidence_id:
            flags.append({"claim": claim.statement, "reason": "missing_evidence_id", "evidence_ids": []})
        elif linked.evidence_id not in evidence_by_id:
            flags.append({"claim": claim.statement, "reason": "evidence_not_available", "evidence_ids": [claim.evidence_id]})
        elif not linked.verified:
            flags.append({"claim": claim.statement, "reason": "evidence_not_verified", "evidence_ids": [claim.evidence_id]})
        elif linked.observed_at and linked.observed_at < now - timedelta(days=freshness_days):
            flags.append({"claim": claim.statement, "reason": "evidence_stale", "evidence_ids": [claim.evidence_id]})
        elif not linked.source:
            flags.append({"claim": claim.statement, "reason": "evidence_missing_source", "evidence_ids": [claim.evidence_id]})
    if suppressed or opted_out:
        flags.append({"claim": "recipient", "reason": "recipient_suppressed_or_opted_out", "evidence_ids": []})
    if existing_customer:
        flags.append({"claim": "recipient", "reason": "existing_customer_excluded_from_cold_outreach", "evidence_ids": []})
    status = "blocked" if suppressed or opted_out or existing_customer else "flagged" if flags else "valid"
    return ClaimCheck(status, tuple(flags), tuple(dict.fromkeys(item for item in ids if item)))


def _first_evidence(request: EmailDraftRequest) -> MessageEvidence | None:
    verified = [item for item in request.prospect_evidence if item.verified and item.about_prospect]
    triggers = [item for item in verified if any(term in item.statement.casefold() for term in ("hiring", "funded", "funding", "migration", "launch", "expansion", "requirement", "appointed"))]
    return (triggers or verified or [None])[0]


def draft_email(request: EmailDraftRequest, *, now: datetime | None = None) -> EmailDraft:
    """Generate a reviewable draft; `send_allowed` is permanently false."""
    now = now or datetime.now(timezone.utc)
    framework = request.framework if request.framework in FRAMEWORKS else "trigger-first"
    selected = _first_evidence(request)
    claims = tuple(request.prospect_evidence)
    check = check_message_claims(claims, request.prospect_evidence, suppressed=request.suppressed, opted_out=request.opted_out, existing_customer=request.existing_customer, now=now)
    if selected and selected.evidence_id not in check.evidence_ids:
        check = ClaimCheck("flagged", check.flagged_claims + ({"claim": selected.statement, "reason": "selected_evidence_not_valid", "evidence_ids": [selected.evidence_id]},), check.evidence_ids)
    company = request.company_name or "your team"
    role = request.buyer_role or "your role"
    if selected and check.approval_status == "valid":
        opener = {"text": f"I noticed {selected.statement}", "evidence_ids": [selected.evidence_id]}
        hypothesis = {"text": f"I’m wondering whether that creates a {role}-level priority around {request.customer_product}; is that relevant?", "evidence_ids": [selected.evidence_id]}
        subject = f"{company}: a question"
        value = {"text": request.approved_positioning, "evidence_ids": list(request.positioning_evidence_ids)}
        if framework == "PAS":
            body = f"{opener['text']}.\n\nThat can create avoidable pressure for {role}. {request.approved_positioning}\n\n{hypothesis['text']}"
        elif framework == "BAB":
            body = f"{opener['text']}.\n\nIf that is a priority, the desired state is a simpler way to address it. {request.approved_positioning}\n\n{hypothesis['text']}"
        elif framework == "AIDA":
            body = f"{opener['text']}. {hypothesis['text']}\n\n{request.approved_positioning}\n\n{hypothesis['text']}"
        else:
            body = f"{opener['text']}. {hypothesis['text']}\n\n{request.approved_positioning}"
        cta = "Worth comparing notes?"
    else:
        opener = {"text": "No evidence-grounded opener is available.", "evidence_ids": []}
        hypothesis = {"text": "No prospect problem hypothesis is drafted until verified evidence is supplied.", "evidence_ids": []}
        value = {"text": request.approved_positioning, "evidence_ids": list(request.positioning_evidence_ids)}
        subject = "draft requires evidence"
        body = "Draft blocked from personalized use until the recipient and prospect evidence are reviewed."
        cta = ""
    followups = () if request.follow_up_count <= 0 or check.approval_status != "valid" else ({"variant": "short", "body": f"Following up on my note about {company}; is this worth discussing?", "evidence_ids": list(check.evidence_ids)},)
    flags = list(check.flagged_claims)
    if not request.positioning_evidence_ids:
        flags.append({"claim": request.approved_positioning, "reason": "approved_positioning_evidence_id_missing", "evidence_ids": []})
    status = "blocked" if check.approval_status == "blocked" else "needs_evidence" if flags else "draft_ready"
    return EmailDraft(request.opportunity_id, request.buyer_id, framework, subject, opener, hypothesis, value, body, cta, followups, tuple(dict.fromkeys(check.evidence_ids + request.positioning_evidence_ids)), tuple(flags), status, False)


def safe_contract(name: str, payload: dict[str, Any], transport: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None) -> dict[str, Any]:
    """Use an injected draft/follow-up adapter only; never expose a send operation."""
    if name not in CONTRACTS:
        raise ValueError(f"unknown cold-email contract: {name}")
    if transport is None:
        return {"status": "disabled", "contract": name, "reason": "Neyvro email draft adapter is not configured", "data": None, "send_allowed": False}
    result = transport(name, payload)
    result["send_allowed"] = False
    return result
