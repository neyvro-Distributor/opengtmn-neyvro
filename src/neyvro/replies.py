"""Thread-aware reply classification and follow-up stop handling."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from threading import RLock
from typing import Any, Callable

CONTRACTS = ("neyvro_get_conversation", "neyvro_get_reply_status", "neyvro_classify_reply", "neyvro_draft_reply", "neyvro_get_followup_queue")


class ReplyCategory(StrEnum):
    INTERESTED = "INTERESTED"
    REQUEST_INFORMATION = "REQUEST_INFORMATION"
    NOT_NOW = "NOT_NOW"
    OBJECTION = "OBJECTION"
    REFERRAL = "REFERRAL"
    WRONG_PERSON = "WRONG_PERSON"
    NOT_INTERESTED = "NOT_INTERESTED"
    UNSUBSCRIBE = "UNSUBSCRIBE"
    OUT_OF_OFFICE = "OUT_OF_OFFICE"
    MEETING_REQUEST = "MEETING_REQUEST"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Message:
    message_id: str
    tenant_id: str
    conversation_id: str
    thread_id: str
    sender: str
    recipient: str
    body: str
    received_at: datetime
    inbound: bool = True


@dataclass(frozen=True)
class Conversation:
    conversation_id: str
    tenant_id: str
    thread_id: str
    messages: tuple[Message, ...] = ()
    followup_id: str | None = None


@dataclass(frozen=True)
class ReplyResult:
    status: str
    conversation_id: str | None
    thread_id: str | None
    reply_id: str
    category: str
    confidence: float
    classification_evidence: tuple[dict[str, str], ...]
    followup_stop: dict[str, Any]
    suppression: dict[str, Any]
    suggested_next_action: str
    draft: dict[str, Any] | None
    approval_status: str
    send_allowed: bool = False

    def as_dict(self) -> dict[str, Any]:
        result = self.__dict__.copy()
        result["classification_evidence"] = list(self.classification_evidence)
        return result


@dataclass
class ReplyProcessor:
    processed_webhooks: set[str] = field(default_factory=set)
    stopped_followups: dict[str, str] = field(default_factory=dict)
    suppressed_recipients: set[str] = field(default_factory=set)
    _lock: RLock = field(default_factory=RLock, repr=False)

    def process(self, conversation: Conversation | None, reply: Message, tenant_id: str, webhook_id: str) -> ReplyResult:
        with self._lock:
            if webhook_id in self.processed_webhooks:
                return ReplyResult("duplicate", conversation.conversation_id if conversation else None, conversation.thread_id if conversation else None, reply.message_id, ReplyCategory.UNKNOWN.value, 0.0, (), {"required": True, "status": "already_stopped_or_processed", "reason": "duplicate_webhook"}, {"required": False, "status": "unchanged"}, "no_action", None, "blocked")
            self.processed_webhooks.add(webhook_id)
            if conversation is None or conversation.tenant_id != tenant_id or reply.tenant_id != tenant_id:
                return ReplyResult("not_found", None, None, reply.message_id, ReplyCategory.UNKNOWN.value, 0.0, (), {"required": False, "status": "not_applied", "reason": "conversation_not_available"}, {"required": False, "status": "unchanged"}, "human_review", None, "blocked")
            if reply.conversation_id != conversation.conversation_id or reply.thread_id != conversation.thread_id:
                return ReplyResult("wrong_thread", conversation.conversation_id, conversation.thread_id, reply.message_id, ReplyCategory.UNKNOWN.value, 0.0, (), {"required": False, "status": "not_applied", "reason": "wrong_email_thread"}, {"required": False, "status": "unchanged"}, "verify_thread", None, "blocked")
            category, confidence, evidence = classify_reply(reply.body)
            self.stopped_followups[conversation.conversation_id] = "reply_detected"
            safety = category in {ReplyCategory.UNSUBSCRIBE, ReplyCategory.NOT_INTERESTED}
            if safety:
                self.suppressed_recipients.add(reply.sender.casefold())
            return ReplyResult("classified", conversation.conversation_id, conversation.thread_id, reply.message_id, category.value, confidence, ({"span": evidence, "source": reply.message_id},), {"required": True, "status": "stopped", "reason": "reply_detected"}, {"required": safety, "status": "suppressed" if safety else "unchanged", "reason": category.value.lower() if safety else None}, suggested_action(category), None, "review_required" if category not in {ReplyCategory.UNSUBSCRIBE, ReplyCategory.NOT_INTERESTED} else "blocked")


def classify_reply(body: str) -> tuple[ReplyCategory, float, str]:
    """Deterministic baseline classifier; production adapters may supply a reviewed classifier."""
    text = " ".join(body.casefold().split())
    rules = (
        (("unsubscribe", "remove me", "stop emailing", "do not contact"), ReplyCategory.UNSUBSCRIBE, 0.99),
        (("not interested", "no thanks", "please don't", "not a fit"), ReplyCategory.NOT_INTERESTED, 0.98),
        (("out of office", "automatic reply", "away until", "returning on"), ReplyCategory.OUT_OF_OFFICE, 0.98),
        (("not the right person", "wrong person", "doesn't handle", "don't own"), ReplyCategory.WRONG_PERSON, 0.95),
        (("you should speak to", "talk to", "contact dana", "i'd suggest"), ReplyCategory.REFERRAL, 0.92),
        (("book", "schedule", "calendar", "meeting", "thursday works"), ReplyCategory.MEETING_REQUEST, 0.94),
        (("tell me more", "interested", "sounds good", "yes,", "sure"), ReplyCategory.INTERESTED, 0.9),
        (("send information", "send info", "more information", "deck", "case study"), ReplyCategory.REQUEST_INFORMATION, 0.9),
        (("next quarter", "not now", "later", "circle back", "in q3"), ReplyCategory.NOT_NOW, 0.9),
        (("budget", "already use", "competitor", "priority", "too expensive"), ReplyCategory.OBJECTION, 0.88),
    )
    for phrases, category, confidence in rules:
        for phrase in phrases:
            if phrase in text:
                return category, confidence, phrase
    return ReplyCategory.UNKNOWN, 0.4, body[:120]


def suggested_action(category: ReplyCategory) -> str:
    return {
        ReplyCategory.INTERESTED: "human_review_meeting_options",
        ReplyCategory.MEETING_REQUEST: "human_review_meeting_options",
        ReplyCategory.REQUEST_INFORMATION: "draft_one_resource_and_soft_next_step",
        ReplyCategory.OBJECTION: "draft_acknowledge_reframe_once",
        ReplyCategory.NOT_NOW: "set_reviewable_reminder_and_exit_active_followup",
        ReplyCategory.REFERRAL: "request_or_route_to_referred_buyer",
        ReplyCategory.WRONG_PERSON: "ask_for_responsible_person",
        ReplyCategory.OUT_OF_OFFICE: "record_return_date_and_pause",
        ReplyCategory.NOT_INTERESTED: "suppress_and_stop",
        ReplyCategory.UNSUBSCRIBE: "suppress_immediately_and_stop",
        ReplyCategory.UNKNOWN: "human_review",
    }[category]


def draft_reply(result: ReplyResult, sender_availability: tuple[str, ...] = (), approved_material: str | None = None) -> dict[str, Any]:
    """Create a reviewable reply draft; unsubscribe/rejection and unknown stay blocked."""
    if result.category in {ReplyCategory.UNSUBSCRIBE.value, ReplyCategory.NOT_INTERESTED.value, ReplyCategory.UNKNOWN.value}:
        return {"status": "blocked", "category": result.category, "body": "", "approval_status": "blocked", "send_allowed": False}
    if result.category in {ReplyCategory.INTERESTED.value, ReplyCategory.MEETING_REQUEST.value}:
        times = ", ".join(sender_availability[:2]) if sender_availability else "two times that the sender has confirmed"
        body = f"Thanks for getting back to me. I can offer {times}; would either work?"
    elif result.category == ReplyCategory.OBJECTION.value:
        body = f"That makes sense. {approved_material or 'I can share a concise explanation of the relevant approach.'} Would a short conversation help assess whether it is relevant?"
    elif result.category == ReplyCategory.REQUEST_INFORMATION.value:
        body = f"Happy to share one relevant resource. {approved_material or 'I will send the approved material for your review.'} Would it be useful to compare notes afterward?"
    elif result.category == ReplyCategory.WRONG_PERSON.value:
        body = "Thanks for letting me know. Who is the right person for this area?"
    elif result.category == ReplyCategory.REFERRAL.value:
        body = "Thanks for pointing me in the right direction. I’ll follow the appropriate introduction path."
    else:
        body = "Thanks for the update. I’ll pause the active follow-up and revisit at the appropriate time."
    return {"status": "draft_ready", "category": result.category, "body": body, "approval_status": "review_required", "send_allowed": False}


def safe_contract(name: str, payload: dict[str, Any], transport: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None) -> dict[str, Any]:
    """Call an injected Gmail/Microsoft/follow-up adapter, otherwise fail closed."""
    if name not in CONTRACTS:
        raise ValueError(f"unknown reply contract: {name}")
    if transport is None:
        return {"status": "disabled", "contract": name, "reason": "Neyvro message-sync/follow-up adapter is not configured", "data": None, "send_allowed": False}
    result = transport(name, payload)
    result["send_allowed"] = False
    return result
