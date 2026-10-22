"""Read-only sender-safety and deliverability assessment."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

CONTRACTS = ("neyvro_get_mailbox_health", "neyvro_get_sender_limits", "neyvro_get_delivery_metrics", "neyvro_audit_email_configuration")
AUTH_STATES = {"verified", "missing", "failed", "unknown"}


@dataclass(frozen=True)
class MailboxHealth:
    provider: str = "unknown"
    connected: bool = False
    authorized: bool = False
    sender_identity: str | None = None
    sending_domain: str | None = None
    observed_at: datetime | None = None
    source: str | None = None


@dataclass(frozen=True)
class AuthenticationStatus:
    spf: str = "unknown"
    dkim: str = "unknown"
    dmarc: str = "unknown"
    dns_authorized: bool = False
    observed_at: datetime | None = None
    source: str | None = None


@dataclass(frozen=True)
class SenderLimits:
    daily_limit: int | None = None
    sent_today: int | None = None
    remaining: int | None = None
    ramp_stage: str | None = None
    throttled: bool | None = None
    observed_at: datetime | None = None
    source: str | None = None


@dataclass(frozen=True)
class DeliveryMetrics:
    bounce_count: int | None = None
    complaint_count: int | None = None
    unsubscribe_count: int | None = None
    delivered_count: int | None = None
    window: str | None = None
    repeated_bounces: int | None = None
    observed_at: datetime | None = None
    source: str | None = None


@dataclass(frozen=True)
class RecipientSafety:
    unverified: int = 0
    suppressed: int = 0
    repeated_bounces: int = 0
    catch_all: int = 0
    opted_out: int = 0


@dataclass(frozen=True)
class DeliverabilityAudit:
    status: str
    provider: str
    verified_configuration_checks: tuple[dict[str, Any], ...]
    provider_health_signals: tuple[dict[str, Any], ...]
    recommendations: tuple[str, ...]
    unknown_metrics: tuple[str, ...]
    recipient_safety: dict[str, int]
    sender_limits: dict[str, Any]
    authentication: dict[str, str]
    send_allowed: bool = False

    def as_dict(self) -> dict[str, Any]:
        result = self.__dict__.copy()
        for field in ("verified_configuration_checks", "provider_health_signals", "recommendations", "unknown_metrics"):
            result[field] = list(result[field])
        return result


def _check(name: str, status: str, source: str | None, observed_at: datetime | None, detail: str) -> dict[str, Any]:
    return {"check": name, "status": status, "detail": detail, "source": source, "observed_at": observed_at.isoformat() if observed_at else None}


def audit_deliverability(mailbox: MailboxHealth, auth: AuthenticationStatus = AuthenticationStatus(), limits: SenderLimits = SenderLimits(), metrics: DeliveryMetrics = DeliveryMetrics(), recipients: RecipientSafety = RecipientSafety()) -> DeliverabilityAudit:
    """Assess only supplied/provider-reported facts; no DNS lookup or send occurs."""
    verified: list[dict[str, Any]] = []
    signals: list[dict[str, Any]] = []
    recommendations: list[str] = []
    unknown: list[str] = []
    hard_block = False
    if not mailbox.connected or not mailbox.authorized:
        verified.append(_check("mailbox_connection", "failed", mailbox.source, mailbox.observed_at, "Gmail or Microsoft mailbox is disconnected or not authorized."))
        hard_block = True
    else:
        verified.append(_check("mailbox_connection", "verified", mailbox.source, mailbox.observed_at, "Authorized mailbox connection reported."))
    if not mailbox.sender_identity:
        unknown.append("sender identity")
    else:
        verified.append(_check("sender_identity", "verified", mailbox.source, mailbox.observed_at, "Sender identity supplied by the authorized mailbox."))
    if not mailbox.sending_domain:
        unknown.append("sending domain")
    for name, value in (("SPF", auth.spf), ("DKIM", auth.dkim), ("DMARC", auth.dmarc)):
        state = value if value in AUTH_STATES else "unknown"
        if not auth.dns_authorized:
            state = "unknown"
            unknown.append(f"{name} (DNS inspection not authorized)")
        verified.append(_check(name, state, auth.source, auth.observed_at, f"{name} status is {state}; no DNS mutation performed."))
        if state in {"missing", "failed"}:
            hard_block = True
            recommendations.append(f"Resolve {name} configuration before sending.")
    if limits.daily_limit is None or limits.sent_today is None:
        unknown.append("sender daily limits")
    else:
        remaining = limits.remaining if limits.remaining is not None else max(0, limits.daily_limit - limits.sent_today)
        signals.append({"signal": "sender_limits", "daily_limit": limits.daily_limit, "sent_today": limits.sent_today, "remaining": remaining, "ramp_stage": limits.ramp_stage, "throttled": limits.throttled, "source": limits.source, "observed_at": limits.observed_at.isoformat() if limits.observed_at else None})
        if limits.sent_today >= limits.daily_limit or limits.throttled:
            hard_block = True
            recommendations.append("Pause sending and wait for the provider limit/throttle to clear.")
        elif limits.ramp_stage in {"new", "warming"}:
            recommendations.append("Use gradual, evenly paced ramp-up; warmup does not guarantee deliverability.")
    for label, value in (("bounce_count", metrics.bounce_count), ("complaint_count", metrics.complaint_count), ("unsubscribe_count", metrics.unsubscribe_count), ("repeated_bounces", metrics.repeated_bounces)):
        if value is None:
            unknown.append(label)
        else:
            signals.append({"signal": label, "value": value, "window": metrics.window, "source": metrics.source, "observed_at": metrics.observed_at.isoformat() if metrics.observed_at else None})
    if metrics.repeated_bounces and metrics.repeated_bounces > 0:
        hard_block = True
        recommendations.append("Stop using repeatedly bouncing recipients and investigate list quality before resuming.")
    if metrics.complaint_count and metrics.complaint_count > 0:
        hard_block = True
        recommendations.append("Pause the affected audience and review complaint causes and consent/expectation alignment.")
    if recipients.unverified or recipients.catch_all:
        hard_block = True
        recommendations.append("Remove or separately review unverified and catch-all recipients before sending.")
    if recipients.suppressed or recipients.opted_out:
        hard_block = True
        recommendations.append("Honor suppression and unsubscribe state immediately; do not send to those recipients.")
    if metrics.bounce_count is None and metrics.complaint_count is None:
        unknown.append("provider delivery health")
    status = "blocked" if hard_block else "review" if unknown else "ready"
    return DeliverabilityAudit(status, mailbox.provider, tuple(verified), tuple(signals), tuple(dict.fromkeys(recommendations)), tuple(dict.fromkeys(unknown)), {"unverified": recipients.unverified, "suppressed": recipients.suppressed, "repeated_bounces": recipients.repeated_bounces, "catch_all": recipients.catch_all, "opted_out": recipients.opted_out}, {"daily_limit": limits.daily_limit, "sent_today": limits.sent_today, "remaining": limits.remaining, "ramp_stage": limits.ramp_stage}, {"spf": auth.spf if auth.dns_authorized and auth.spf in AUTH_STATES else "unknown", "dkim": auth.dkim if auth.dns_authorized and auth.dkim in AUTH_STATES else "unknown", "dmarc": auth.dmarc if auth.dns_authorized and auth.dmarc in AUTH_STATES else "unknown"}, False)


def safe_contract(name: str, payload: dict[str, Any], transport: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None) -> dict[str, Any]:
    """Call an injected read-only adapter, otherwise fail closed."""
    if name not in CONTRACTS:
        raise ValueError(f"unknown deliverability contract: {name}")
    if transport is None:
        return {"status": "disabled", "contract": name, "reason": "Neyvro mailbox/deliverability adapter is not configured", "data": None, "send_allowed": False}
    result = transport(name, payload)
    result["send_allowed"] = False
    return result
