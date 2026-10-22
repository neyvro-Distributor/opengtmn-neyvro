"""Evidence-grounded content planning and approval-gated publication proposals."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

CONTRACTS = (
    "neyvro_generate_content_ideas",
    "neyvro_create_content_brief",
    "neyvro_draft_content",
    "neyvro_get_content_calendar",
    "neyvro_propose_social_post",
)
STATES = ("DRAFT", "READY_FOR_REVIEW", "APPROVED", "SCHEDULED", "PUBLISHED", "FAILED")
CHANNELS = {"website_blog", "x", "reddit", "linkedin_assisted", "substack", "authorized_api"}


@dataclass(frozen=True)
class ContentContext:
    product_name: str
    buyer_questions: tuple[str, ...] = ()
    audience: tuple[str, ...] = ()
    positioning: str | None = None
    approved_claims: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    brand_voice: str | None = None
    brand_voice_version: str | None = None
    channels: tuple[str, ...] = ()


@dataclass(frozen=True)
class ContentIdea:
    idea_id: str
    title: str
    buyer_question: str
    audience: str
    buyer_stage: str
    format: str
    evidence: tuple[str, ...] = ()
    confidence: str = "needs_research"

    def as_dict(self) -> dict[str, Any]:
        result = self.__dict__.copy()
        result["evidence"] = list(self.evidence)
        return result


@dataclass(frozen=True)
class ContentBrief:
    brief_id: str
    idea: ContentIdea
    outline: tuple[str, ...]
    claims_to_verify: tuple[str, ...]
    distribution: tuple[dict[str, Any], ...]
    status: str = "DRAFT"

    def as_dict(self) -> dict[str, Any]:
        result = self.__dict__.copy()
        result["idea"] = self.idea.as_dict()
        result["outline"] = list(self.outline)
        result["claims_to_verify"] = list(self.claims_to_verify)
        result["distribution"] = list(self.distribution)
        return result


def generate_content_ideas(context: ContentContext, limit: int = 10) -> tuple[ContentIdea, ...]:
    """Turn supplied buyer questions into deterministic, evidence-linked ideas."""
    if limit < 1:
        raise ValueError("limit must be positive")
    questions = context.buyer_questions or ("What problem does this product category solve?",)
    audiences = context.audience or ("prospective buyer",)
    ideas = []
    for index, question in enumerate(questions[:limit], 1):
        stage = "awareness" if index % 3 == 1 else "consideration" if index % 3 == 2 else "decision"
        fmt = "guide" if stage == "awareness" else "comparison" if stage == "consideration" else "checklist"
        ideas.append(ContentIdea(f"idea-{index:03d}", question.rstrip("?").strip().capitalize(), question, audiences[(index - 1) % len(audiences)], stage, fmt, context.evidence, "supported" if context.evidence else "needs_research"))
    return tuple(ideas)


def create_content_brief(context: ContentContext, idea: ContentIdea, *, channels: tuple[str, ...] | None = None) -> ContentBrief:
    selected = channels if channels is not None else context.channels
    distribution = tuple({"channel": channel, "status": "authorized_check_required", "external_action_executed": False} for channel in selected)
    claims = () if context.approved_claims else ("product capability and outcome claims require verification",)
    return ContentBrief(f"brief-{idea.idea_id}", idea, ("Direct answer", "Context and definitions", "Evidence and practical steps", "Limitations", "Next step"), claims, distribution)


def draft_content(context: ContentContext, brief: ContentBrief, body: str, *, channel: str = "website_blog") -> dict[str, Any]:
    """Return a draft and claim review; never publish or infer engagement."""
    if channel not in CHANNELS:
        return {"status": "unsupported", "state": "FAILED", "channel": channel, "external_action_executed": False, "draft": None}
    supported = [claim for claim in context.approved_claims if claim.casefold() in body.casefold()]
    unsupported = [] if context.approved_claims else ["No approved product claims were supplied"]
    return {"status": "needs_review" if unsupported else "drafted", "state": "DRAFT", "channel": channel, "draft": body, "claim_review": {"supported": supported, "needs_verification": list(brief.claims_to_verify), "unsupported": unsupported}, "brand_voice": {"version": context.brand_voice_version, "status": "provided" if context.brand_voice else "unknown"}, "evidence": list(context.evidence), "external_action_executed": False}


def get_calendar(items: tuple[dict[str, Any], ...], *, publication_history: tuple[str, ...] = ()) -> dict[str, Any]:
    """Validate calendar records and flag duplicate publication keys."""
    seen: set[str] = set(publication_history)
    result = []
    for item in items:
        key = str(item.get("publication_key", ""))
        duplicate = not key or key in seen
        result.append({**item, "state": item.get("state", "DRAFT"), "duplicate": duplicate})
        if key:
            seen.add(key)
    return {"status": "partial" if any(item["duplicate"] for item in result) else "available", "items": result, "external_action_executed": False}


def propose_social_post(channel: str, content: str, *, authorized: bool, approved: bool, publication_key: str, existing_keys: tuple[str, ...] = ()) -> dict[str, Any]:
    if channel not in CHANNELS:
        return {"status": "unsupported", "state": "FAILED", "external_action_executed": False}
    if not authorized:
        return {"status": "unauthorized", "state": "DRAFT", "external_action_executed": False}
    if not approved:
        return {"status": "approval_required", "state": "READY_FOR_REVIEW", "external_action_executed": False}
    if not publication_key or publication_key in existing_keys:
        return {"status": "duplicate", "state": "FAILED", "external_action_executed": False}
    return {"status": "proposed", "state": "APPROVED", "channel": channel, "content": content, "publication_key": publication_key, "review_required": True, "external_action_executed": False}


def safe_contract(name: str, payload: dict[str, Any], transport: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None) -> dict[str, Any]:
    if name not in CONTRACTS:
        raise ValueError(f"unknown content contract: {name}")
    if transport is None:
        return {"status": "disabled", "contract": name, "reason": "Neyvro content adapter is not configured", "data": None, "external_action_executed": False}
    result = transport(name, payload)
    result["external_action_executed"] = False
    return result
