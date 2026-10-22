from datetime import datetime, timezone

from neyvro.outbound_metrics import OutboundEvent, compare_contextual_benchmark, compute_metrics, safe_contract


START = datetime(2026, 1, 1, tzinfo=timezone.utc)
END = datetime(2026, 1, 31, tzinfo=timezone.utc)


def event(event_id, kind, entity_id, *, tenant="t1", value=None, dimensions=(), automatic=False):
    return OutboundEvent(event_id, tenant, kind, START, entity_id, dimensions=dimensions, value=value, automatic=automatic)


def test_funnel_metrics_have_explicit_denominators_and_rates():
    events = (
        event("c1", "contact_found", "contact-1"),
        event("v1", "contact_verified", "contact-1"),
        event("a1", "outreach_attempt", "attempt-1"),
        event("d1", "delivered", "attempt-1"),
        event("r1", "reply", "attempt-1"),
        event("p1", "positive_reply", "attempt-1"),
        event("m1", "meeting_booked", "attempt-1"),
        event("o1", "qualified_opportunity", "opp-1", value=12000),
        event("w1", "won", "opp-1"),
        event("cost1", "campaign_cost", "cost-1", value=100),
        event("rev1", "revenue_attributed", "opp-1", value=12000),
    )

    result = compute_metrics(events, "t1", START, END)

    assert result["metrics"]["delivery_rate"]["numerator"] == 1
    assert result["metrics"]["delivery_rate"]["denominator"] == 1
    assert result["metrics"]["positive_reply_rate"]["rate"] == 1
    assert result["metrics"]["pipeline_value"]["numerator"] == 12000
    assert result["metrics"]["cost_per_qualified_opportunity"]["rate"] == 100
    assert result["metrics"]["revenue_attribution"]["numerator"] == 12000
    assert "time_window" in result["metrics"]["reply_rate"]
    assert result["open_rate_note"].startswith("Open rate is not")


def test_zero_denominator_is_unavailable_not_zero():
    result = compute_metrics((), "t1", START, END)

    assert result["metrics"]["delivery_rate"]["denominator"] == 0
    assert result["metrics"]["delivery_rate"]["rate"] is None
    assert result["metrics"]["delivery_rate"]["status"] == "unavailable"
    assert result["metrics"]["won_outcomes"]["status"] == "unavailable"
    assert any("CRM won/lost" in warning for warning in result["data_quality"]["warnings"])


def test_duplicates_and_inconsistent_events_are_reported():
    events = (
        event("a1", "outreach_attempt", "attempt-1"),
        event("a1", "outreach_attempt", "attempt-1"),
        event("r1", "reply", "orphan-reply"),
        event("auto", "reply", "attempt-1", automatic=True),
    )

    result = compute_metrics(events, "t1", START, END)

    assert result["status"] == "partial"
    assert result["data_quality"]["deduplicated"] is True
    assert any("duplicate" in warning for warning in result["data_quality"]["warnings"])
    assert any("no delivered" in warning for warning in result["data_quality"]["warnings"])
    assert any("automatic" in warning for warning in result["data_quality"]["warnings"])


def test_segments_and_tenants_are_isolated():
    events = (
        event("a1", "outreach_attempt", "a1", dimensions=(("industry", "security"),)),
        event("d1", "delivered", "a1", dimensions=(("industry", "security"),)),
        event("other", "outreach_attempt", "other", tenant="t2", dimensions=(("industry", "security"),)),
        event("dev", "outreach_attempt", "dev", dimensions=(("industry", "developer"),)),
    )

    result = compute_metrics(events, "t1", START, END, segment={"industry": "security"})

    assert result["tenant_scope"] == "t1"
    assert result["metrics"]["outreach_attempts"]["numerator"] == 1
    assert result["metrics"]["delivery_rate"]["numerator"] == 1


def test_benchmark_requires_source_and_is_contextual_not_a_target():
    metric = {"rate": 0.04}
    assert compare_contextual_benchmark(metric, {"low": 0.03, "high": 0.05})["status"] == "unavailable"
    comparison = compare_contextual_benchmark(metric, {"low": 0.03, "high": 0.05, "source": "study-1", "population": "B2B SaaS", "denominator": "delivered"})
    assert comparison["within_range"] is True
    assert comparison["not_a_guarantee"] is True


def test_recommendations_respect_sample_size():
    result = compute_metrics((event("a1", "outreach_attempt", "a1"),), "t1", START, END)

    assert any(item["confidence"] == "insufficient_sample" for item in result["recommendations"])


def test_analytics_contract_is_disabled_without_adapter():
    result = safe_contract("neyvro_get_campaign_metrics", {"tenant_id": "t1"})

    assert result["status"] == "disabled"
    assert result["data"] is None
