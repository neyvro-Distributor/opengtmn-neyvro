from datetime import datetime, timedelta, timezone

from neyvro.lead_sourcing import AccountCandidate, EnrichmentPolicy, ProviderContact, ProviderResult, safe_contract, source_and_enrich

NOW = datetime(2026, 10, 23, tzinfo=timezone.utc)


def contact(record, company_id="c1", email="alex@example.com", provenance="provider_verified", status="verified", days=1, **kwargs):
    cost_units = kwargs.pop("cost_units", 1)
    return ProviderContact("Alex Morgan", "Example Inc", company_id, "VP Engineering", "provider", record, email, provenance, status, NOW - timedelta(days=days), buyer_category="economic_buyer", permitted_use=True, permitted_use_basis="B2B provider terms", cost_units=cost_units, **kwargs)


def test_icp_selection_and_structured_verified_response():
    result = source_and_enrich((AccountCandidate("c1", "Example Inc", "example.com"), AccountCandidate("customer", "Customer", "customer.com", existing_customer=True), AccountCandidate("weak", "Weak", "weak.com", icp_status="incomplete")), (ProviderResult("crm", (contact("r1"),)),), EnrichmentPolicy(), NOW)
    assert result.accounts_considered == ("c1",)
    assert {item["reason"] for item in result.accounts_excluded} == {"existing_customer", "icp_incomplete"}
    assert result.contacts[0]["verification_status"] == "verified"
    assert result.contacts[0]["contact_details"]["permitted_use"] is True
    assert set(result.as_dict()) == {"accounts_considered", "accounts_excluded", "contacts", "duplicates_removed", "suppressed_contacts", "provider_events", "usage", "research_gaps"}


def test_guessed_email_is_never_verified_and_catch_all_is_risky():
    result = source_and_enrich((AccountCandidate("c1", "Example Inc", "example.com"),), (ProviderResult("finder", (contact("guess", email="alex@example.com", provenance="pattern_guess"), contact("catch", email="sam@example.com", status="catch_all"))),), EnrichmentPolicy(), NOW)
    statuses = {item["source"]["record_id"]: item["verification_status"] for item in result.contacts}
    assert statuses == {"guess": "unverified", "catch": "catch_all"}


def test_duplicates_wrong_company_and_suppression_are_removed():
    result = source_and_enrich((AccountCandidate("c1", "Example Inc", "example.com"),), (ProviderResult("one", (contact("first"), contact("wrong", company_id="other"))), ProviderResult("two", (contact("duplicate"), contact("opt", email="opt@example.com", status="opted_out")))), EnrichmentPolicy(suppressed_emails=frozenset({"opt@example.com"})), NOW)
    assert len(result.contacts) == 1
    assert "duplicate" in result.duplicates_removed
    assert "opt" in result.suppressed_contacts
    assert any(item["record_id"] == "wrong" for item in result.provider_events)


def test_stale_verification_and_provider_failure_are_reported():
    result = source_and_enrich((AccountCandidate("c1", "Example Inc", "example.com"),), (ProviderResult("crm", (contact("stale", days=60),)), ProviderResult("paid", error="rate limited", rate_limit_remaining=0, paid=True)), EnrichmentPolicy(entitled=True, usage_budget=2), NOW)
    assert result.contacts[0]["verification_status"] == "stale"
    assert result.provider_events[-1]["status"] == "failed"
    assert "provider paid failed" in result.research_gaps


def test_paid_provider_requires_entitlement_and_budget():
    result = source_and_enrich((AccountCandidate("c1", "Example Inc", "example.com"),), (ProviderResult("paid", (contact("paid", cost_units=1),), paid=True),), EnrichmentPolicy(entitled=False), NOW)
    assert not result.contacts
    assert result.provider_events[0]["status"] == "disabled"
    assert "requires customer entitlement" in result.research_gaps[0]


def test_disabled_backend_and_injected_adapter():
    assert safe_contract("neyvro_search_buyers", {"workspace_id": "w1"})["status"] == "disabled"
    result = safe_contract("neyvro_get_contact_verification", {"contact_id": "p1"}, lambda name, payload: {"status": "available", "contract": name, "payload": payload})
    assert result["status"] == "available"
