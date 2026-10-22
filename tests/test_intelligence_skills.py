from datetime import datetime, timezone

from neyvro.intelligence_skills import CompanyTwin, EvidenceRecord, analyze_company_twin, analyze_negative_evidence, attribute_revenue, detect_buying_window, detect_technology_changes, match_buyer_opportunity, plan_continuous_investigation, predict_problem_intelligence, safe_contract, verify_evidence


NOW = datetime(2026, 10, 23, tzinfo=timezone.utc)


def evidence(evidence_id, claim, *, classification="observed_fact", freshness_days=10, tenant="t1"):
    return EvidenceRecord(evidence_id, tenant, claim, classification, "authorized-source", NOW, freshness_days, 0.9)


def test_supported_twin_and_technology_change_use_verified_evidence():
    records = (evidence("e1", "cloud migration announced"), evidence("e2", "security hiring increased"))
    twin = CompanyTwin("t1", "co1", current_state={"industry": "SaaS"}, history=({"date": "2026-10-01", "event": "migration"},), transitions=({"from": "on-prem", "to": "cloud", "evidence_ids": ["e1"]},), evidence=records)

    result = analyze_company_twin(twin)
    changes = detect_technology_changes(({"kind": "migration", "evidence_ids": ["e1"], "gap": "desired security controls"},), records, "t1")

    assert result["status"] == "available"
    assert result["current_state"]["industry"] == "SaaS"
    assert changes["changes"][0]["kind"] == "migration"
    assert changes["technology_gaps"]


def test_conflicting_and_stale_evidence_are_not_upgraded():
    records = (
        evidence("old", "legacy stack remains", freshness_days=300),
        evidence("conflict", "legacy stack remains", classification="contradictory"),
        evidence("other-tenant", "cloud migration", tenant="t2"),
    )

    result = verify_evidence(records, "t1", stale_after_days=180)

    assert result["status"] == "partial"
    assert result["stale_evidence"][0]["evidence_id"] == "old"
    assert result["contradictions"]
    assert all(item["tenant_id"] == "t1" for item in result["verified_claims"] + result["stale_evidence"])


def test_missing_twin_and_prediction_remain_uncertain():
    twin = analyze_company_twin(CompanyTwin("t1", "co1"))
    prediction = predict_problem_intelligence(({"kind": "migration", "possible_problem": "migration risk", "evidence_ids": ["missing"]},), {}, (), "t1")

    assert twin["status"] == "partial"
    assert "current company state" in twin["unknowns"]
    assert prediction["status"] == "partial"
    assert prediction["problem_hypotheses"] == []


def test_prediction_and_buying_window_require_verified_support():
    records = (evidence("e1", "engineering expansion"), evidence("e2", "security requirement changed"))
    changes = ({"kind": "engineering", "possible_problem": "capacity planning", "evidence_ids": ["e1"], "validation_question": "Is capacity a current priority?"},)
    signals = ({"type": "hiring", "evidence_ids": ["e1"]}, {"type": "security", "evidence_ids": ["e2"]})

    prediction = predict_problem_intelligence(changes, {"exclusions": ("no regulated industries",)}, records, "t1")
    window = detect_buying_window(signals, records, "t1")

    assert prediction["problem_hypotheses"][0]["confidence"] == "not_asserted"
    assert prediction["disqualifiers"]
    assert window["status"] == "available"
    assert window["recommended_expiry"] is None


def test_buyer_matching_requires_evidence_and_preserves_missing_roles():
    records = (evidence("e1", "security expansion"),)
    matched = match_buyer_opportunity("security controls", ({"buyer_id": "b1", "responsibility": "CISO", "evidence_ids": ["e1"]},), records, "t1")
    missing = match_buyer_opportunity("security controls", ({"buyer_id": "b2", "responsibility": "CISO", "evidence_ids": ["unknown"]},), records, "t1")

    assert matched["matches"][0]["responsibility"] == "CISO"
    assert missing["status"] == "partial"
    assert missing["missing_stakeholders"]


def test_investigation_respects_budget_and_freshness():
    result = plan_continuous_investigation(
        ({"question": "current stack?"},),
        ({"action": "read-timeline", "cost": 1, "authorized": True}, {"action": "paid-crawl", "cost": 10, "authorized": True}),
        budget_remaining=2,
        fresh=True,
    )

    assert len(result["allowed_actions"]) == 1
    assert len(result["blocked_actions"]) >= 2
    assert result["budget_remaining"] == 2


def test_negative_evidence_and_revenue_attribution_are_bounded():
    records = (evidence("e1", "no security team"),)
    negative = analyze_negative_evidence(({"kind": "negative", "disqualifier": True, "evidence_ids": ["e1"]}, {"kind": "negative", "evidence_ids": ["unknown"]}), records, "t1")
    attribution = attribute_revenue(({"tenant_id": "t1", "opportunity_id": "o1", "value": 500}, {"tenant_id": "t1", "value": 100}, {"tenant_id": "t2", "opportunity_id": "o2", "value": 900}), "t1")

    assert negative["disqualifiers"]
    assert len(negative["not_observed"]) == 1
    assert attribution["attributed_revenue"] == 500
    assert attribution["status"] == "partial"
    assert attribution["unattributed_events"]


def test_unauthorized_twin_and_disabled_contract_fail_closed():
    twin = analyze_company_twin(CompanyTwin("t1", "co1", authorized=False))
    contract = safe_contract("neyvro_get_company_twin", {"company_id": "co1"})

    assert twin["status"] == "blocked"
    assert contract["status"] == "disabled"
    assert contract["data"] is None
