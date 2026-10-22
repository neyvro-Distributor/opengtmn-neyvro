from datetime import datetime, timedelta, timezone

from neyvro.account_research import CompanyTwin, ResearchEvidence, ResearchRequest, research_company, safe_contract

NOW = datetime(2026, 10, 23, tzinfo=timezone.utc)


def ev(eid, category, statement, days=1, polarity="supporting"):
    return ResearchEvidence(eid, f"https://example.test/{eid}", statement, NOW - timedelta(days=days), category, 0.9, polarity)


def test_a_tier_selects_one_evidence_backed_angle_and_budget():
    result = research_company(CompanyTwin("c1", "Acme Security", industry="security", approximate_size="enterprise", business_model="B2B SaaS", buyers=("CISO",), evidence=(ev("h1", "hiring", "Acme opened ten cloud-security roles"), ev("t1", "technology_change", "Acme is migrating workloads to Kubernetes"), ev("n1", "general", "Acme has no public compliance deadline", polarity="negative")), last_researched_at=NOW - timedelta(days=1)), ResearchRequest("A", NOW, used_fetches=2))
    assert result.status == "researched"
    assert result.outreach_angle["status"] == "ready"
    assert result.outreach_angle["evidence_ids"] == ["t1"]
    assert result.research_budget == {"minutes": 15, "source_fetches": 12, "used_fetches": 2}
    assert result.negative_evidence[0]["evidence_id"] == "n1"


def test_contradictory_signals_are_visible_and_block_angle():
    result = research_company(CompanyTwin("c2", "MixedCo", industry="software", business_model="B2B", evidence=(ev("a", "technology_change", "Migrating to AWS"), ev("b", "technology_change", "Decommissioning AWS"))), ResearchRequest("B", NOW))
    assert result.status == "stale"
    assert result.outreach_angle["status"] == "not_ready"
    assert "contradictory fresh signals in technology_change" in result.uncertainty


def test_stale_research_and_unknown_fields_are_not_presented_as_current():
    result = research_company(CompanyTwin("c3", "OldCo", industry="software", evidence=(ev("old", "product", "Launched a product", days=45),), last_researched_at=NOW - timedelta(days=45)), ResearchRequest("B", NOW))
    assert result.status == "stale"
    assert "freshness: existing research is stale and should not be used as a current trigger" in result.unknown_facts
    assert result.outreach_angle["status"] == "not_ready"


def test_nonexistent_and_unauthorized_accounts_fail_closed():
    assert research_company(CompanyTwin("missing", "Missing", exists=False), ResearchRequest("A", NOW)).status == "not_found"
    unauthorized = research_company(CompanyTwin("private", "Private", authorized=False), ResearchRequest("A", NOW))
    assert unauthorized.status == "unauthorized"
    assert "authorized company access" in unauthorized.unknown_facts


def test_research_backend_is_disabled_without_adapter_and_calls_injected_adapter():
    disabled = safe_contract("neyvro_get_company_twin", {"company_id": "c1"})
    assert disabled["status"] == "disabled"
    called = safe_contract("neyvro_get_evidence", {"company_id": "c1"}, lambda name, payload: {"status": "available", "name": name, "payload": payload})
    assert called["status"] == "available"
