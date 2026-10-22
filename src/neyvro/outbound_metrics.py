"""Tenant-safe outbound funnel metrics with explicit denominators and provenance."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Iterable

CONTRACTS = (
    "neyvro_get_campaign_metrics",
    "neyvro_get_pipeline_metrics",
    "neyvro_get_revenue_attribution",
    "neyvro_get_signal_performance",
)


@dataclass(frozen=True)
class OutboundEvent:
    event_id: str
    tenant_id: str
    kind: str
    occurred_at: datetime
    entity_id: str
    campaign_id: str | None = None
    channel: str | None = None
    dimensions: tuple[tuple[str, str], ...] = ()
    value: float | None = None
    currency: str | None = None
    source: str = "neyvro"
    automatic: bool = False

    def dimension_map(self) -> dict[str, str]:
        return dict(self.dimensions)


METRIC_DEFINITIONS = {
    "contacts_found": "unique contacts_found entities / unique contacts_found entities",
    "contact_verification_rate": "unique verified contacts / unique contacts found",
    "outreach_attempts": "unique outreach_attempt entities / unique outreach_attempt entities",
    "delivery_rate": "unique delivered attempts / unique outreach attempts",
    "bounce_rate": "unique bounced attempts / unique outreach attempts",
    "reply_rate": "unique human replies / unique delivered attempts",
    "positive_reply_rate": "unique positive human replies / unique delivered attempts",
    "positive_reply_share": "unique positive human replies / unique human replies",
    "meetings_booked_rate": "unique meetings booked / unique outreach attempts",
    "qualified_opportunity_rate": "unique qualified opportunities / unique outreach attempts",
    "pipeline_value": "sum of authorized opportunity amounts / 1",
    "won_outcomes": "unique won CRM outcomes / unique CRM outcomes recorded",
    "lost_outcomes": "unique lost CRM outcomes / unique CRM outcomes recorded",
    "revenue_attribution": "attributed revenue / 1",
    "cost_per_qualified_opportunity": "authorized campaign cost / unique qualified opportunities",
}


def _metric(name: str, numerator: float, denominator: float, start: datetime, end: datetime, *, segment: dict[str, str], event_ids: Iterable[str], status: str = "available", limitations: Iterable[str] = ()) -> dict[str, Any]:
    rate = None if denominator == 0 else numerator / denominator
    if denominator == 0 and status == "available":
        status = "unavailable"
    return {"metric": name, "numerator": numerator, "denominator": denominator, "rate": rate, "unit": "ratio" if name.endswith("rate") or name.endswith("share") else "count", "time_window": {"start": start.isoformat(), "end": end.isoformat()}, "segment": dict(sorted(segment.items())), "sample_size": int(denominator), "status": status, "definition": METRIC_DEFINITIONS[name], "source_event_ids": sorted(set(event_ids)), "limitations": list(limitations)}


def _unique(events: Iterable[OutboundEvent], kind: str) -> dict[str, OutboundEvent]:
    return {event.entity_id: event for event in events if event.kind == kind}


def compute_metrics(events: tuple[OutboundEvent, ...], tenant_id: str, start: datetime, end: datetime, *, segment: dict[str, str] | None = None) -> dict[str, Any]:
    """Aggregate only the requested tenant/window/segment and retain quality warnings."""
    if end < start:
        raise ValueError("end must not precede start")
    requested = segment or {}
    in_scope = [event for event in events if event.tenant_id == tenant_id and start <= event.occurred_at <= end and all(event.dimension_map().get(key) == value for key, value in requested.items())]
    warnings: list[str] = []
    duplicate_ids = len([event.event_id for event in in_scope]) - len({event.event_id for event in in_scope})
    if duplicate_ids:
        warnings.append(f"ignored {duplicate_ids} duplicate event record(s)")
    deduped = list({event.event_id: event for event in in_scope}.values())
    contacts = _unique(deduped, "contact_found")
    verified = _unique(deduped, "contact_verified")
    attempts = _unique(deduped, "outreach_attempt")
    delivered = _unique(deduped, "delivered")
    bounced = _unique(deduped, "bounced")
    replies = _unique(deduped, "reply")
    positive = _unique(deduped, "positive_reply")
    meetings = _unique(deduped, "meeting_booked")
    opportunities = _unique(deduped, "qualified_opportunity")
    outcomes = {**_unique(deduped, "won"), **_unique(deduped, "lost")}
    attributed = _unique(deduped, "revenue_attributed")
    costs = _unique(deduped, "campaign_cost")
    for reply in replies.values():
        if reply.entity_id not in delivered and reply.entity_id not in attempts:
            warnings.append(f"reply {reply.entity_id} has no delivered or attempt event")
    if any(event.kind == "reply" and event.automatic for event in replies.values()):
        warnings.append("automatic replies were excluded from human reply metrics")
        replies = {key: event for key, event in replies.items() if not event.automatic}
    if not outcomes:
        warnings.append("CRM won/lost outcomes are unavailable for this window")
    metrics: dict[str, dict[str, Any]] = {}
    metrics["contacts_found"] = _metric("contacts_found", len(contacts), 1, start, end, segment=requested, event_ids=(e.event_id for e in contacts.values()))
    metrics["contact_verification_rate"] = _metric("contact_verification_rate", len(set(verified) & set(contacts)), len(contacts), start, end, segment=requested, event_ids=(e.event_id for e in (*contacts.values(), *verified.values())))
    metrics["outreach_attempts"] = _metric("outreach_attempts", len(attempts), 1, start, end, segment=requested, event_ids=(e.event_id for e in attempts.values()))
    metrics["delivery_rate"] = _metric("delivery_rate", len(set(delivered) & set(attempts)), len(attempts), start, end, segment=requested, event_ids=(e.event_id for e in (*attempts.values(), *delivered.values())))
    metrics["bounce_rate"] = _metric("bounce_rate", len(set(bounced) & set(attempts)), len(attempts), start, end, segment=requested, event_ids=(e.event_id for e in (*attempts.values(), *bounced.values())))
    metrics["reply_rate"] = _metric("reply_rate", len(set(replies) & set(delivered)), len(delivered), start, end, segment=requested, event_ids=(e.event_id for e in (*delivered.values(), *replies.values())))
    metrics["positive_reply_rate"] = _metric("positive_reply_rate", len(set(positive) & set(delivered)), len(delivered), start, end, segment=requested, event_ids=(e.event_id for e in (*delivered.values(), *positive.values())))
    metrics["positive_reply_share"] = _metric("positive_reply_share", len(set(positive) & set(replies)), len(replies), start, end, segment=requested, event_ids=(e.event_id for e in (*replies.values(), *positive.values())))
    metrics["meetings_booked_rate"] = _metric("meetings_booked_rate", len(set(meetings) & set(attempts)), len(attempts), start, end, segment=requested, event_ids=(e.event_id for e in (*attempts.values(), *meetings.values())))
    metrics["qualified_opportunity_rate"] = _metric("qualified_opportunity_rate", len(set(opportunities) & set(attempts)), len(attempts), start, end, segment=requested, event_ids=(e.event_id for e in (*attempts.values(), *opportunities.values())))
    metrics["pipeline_value"] = _metric("pipeline_value", sum(event.value or 0 for event in opportunities.values()), 1, start, end, segment=requested, event_ids=(e.event_id for e in opportunities.values()), limitations=("missing opportunity amounts are treated as unknown in production adapters",))
    metrics["won_outcomes"] = _metric("won_outcomes", len(_unique(deduped, "won")), len(outcomes), start, end, segment=requested, event_ids=(e.event_id for e in outcomes.values()))
    metrics["lost_outcomes"] = _metric("lost_outcomes", len(_unique(deduped, "lost")), len(outcomes), start, end, segment=requested, event_ids=(e.event_id for e in outcomes.values()))
    metrics["revenue_attribution"] = _metric("revenue_attribution", sum(event.value or 0 for event in attributed.values()), 1, start, end, segment=requested, event_ids=(e.event_id for e in attributed.values()), limitations=("Requires a customer-declared attribution model.",) if not attributed else ())
    metrics["cost_per_qualified_opportunity"] = _metric("cost_per_qualified_opportunity", sum(event.value or 0 for event in costs.values()), len(opportunities), start, end, segment=requested, event_ids=(e.event_id for e in (*costs.values(), *opportunities.values())), limitations=("Campaign cost records are unavailable." if not costs else "",))
    metrics["cost_per_qualified_opportunity"]["unit"] = "currency_per_qualified_opportunity"
    if not costs:
        metrics["cost_per_qualified_opportunity"]["status"] = "unavailable"
    return {"status": "partial" if warnings else "available", "tenant_scope": tenant_id, "time_window": {"start": start.isoformat(), "end": end.isoformat()}, "segment": dict(sorted(requested.items())), "metrics": metrics, "definitions": METRIC_DEFINITIONS, "data_quality": {"warnings": list(dict.fromkeys(warnings)), "deduplicated": True}, "benchmarks": [], "recommendations": recommend(metrics), "causal_limits": ["Observed segment differences are correlational unless an experiment or credible causal design is supplied."], "open_rate_note": "Open rate is not the primary success metric and is omitted unless provided as a directional diagnostic."}


def recommend(metrics: dict[str, dict[str, Any]], *, minimum_sample: int = 30) -> list[dict[str, Any]]:
    recommendations = []
    for name in ("bounce_rate", "reply_rate", "positive_reply_rate", "meetings_booked_rate", "qualified_opportunity_rate"):
        item = metrics.get(name)
        if not item:
            continue
        if item["sample_size"] < minimum_sample:
            recommendations.append({"metric": name, "action": "collect more observations before changing strategy", "sample_size": item["sample_size"], "confidence": "insufficient_sample"})
    if metrics.get("bounce_rate", {}).get("rate") is not None and metrics["bounce_rate"]["rate"] >= 0.02:
        recommendations.append({"metric": "bounce_rate", "action": "pause scaling and audit contact verification and suppression handling", "confidence": "observed_guardrail"})
    if metrics.get("positive_reply_rate", {}).get("rate") is not None and metrics["positive_reply_rate"]["rate"] < 0.01:
        recommendations.append({"metric": "positive_reply_rate", "action": "review ICP fit, evidence-backed personalization, and message relevance before increasing volume", "confidence": "directional"})
    return recommendations


def compare_contextual_benchmark(metric: dict[str, Any], benchmark: dict[str, Any]) -> dict[str, Any]:
    """Compare to a supplied range without turning it into a target or causal claim."""
    if not benchmark.get("source") or benchmark.get("low") is None or benchmark.get("high") is None:
        return {"status": "unavailable", "reason": "benchmark source and range are required"}
    value = metric.get("rate")
    return {"status": "contextual", "within_range": value is not None and benchmark["low"] <= value <= benchmark["high"], "source": benchmark["source"], "population": benchmark.get("population"), "denominator": benchmark.get("denominator"), "not_a_guarantee": True}


def safe_contract(name: str, payload: dict[str, Any], transport: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None) -> dict[str, Any]:
    if name not in CONTRACTS:
        raise ValueError(f"unknown outbound metrics contract: {name}")
    if transport is None:
        return {"status": "disabled", "contract": name, "reason": "Neyvro analytics adapter is not configured", "data": None}
    return transport(name, payload)
