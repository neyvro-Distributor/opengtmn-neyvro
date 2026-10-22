from neyvro.geo import GeoSnapshot, audit_geo, propose_geo_improvements, safe_contract


def test_malformed_schema_is_reported_without_visibility_claims():
    audit = audit_geo(GeoSnapshot(
        "https://example.com",
        crawler_access=(("OAI-SearchBot", "allowed"),),
        schema_status="malformed",
    ))

    assert any(item["status"] == "malformed" for item in audit.schema_findings)
    assert audit.visibility_measurements["status"] == "unavailable"
    assert audit.visibility_measurements["data"] is None
    assert "ChatGPT" in audit.unknowns[0]


def test_crawler_and_edge_restriction_conflict_is_explicit():
    audit = audit_geo(GeoSnapshot(
        "https://example.com",
        crawler_access=(("GPTBot", "allowed"), ("ClaudeBot", "blocked")),
        edge_access=(("GPTBot", "blocked"),),
    ))

    assert any("GPTBot" in finding for finding in audit.conflicting_findings)
    assert any(item["status"] == "blocked" for item in audit.access_findings)
    assert audit.status == "partial"


def test_missing_inputs_remain_unknown_and_measurement_plan_is_actionable():
    audit = audit_geo(GeoSnapshot("https://example.com"))

    assert audit.status == "partial"
    assert "AI/search crawler access observations" in audit.unknowns
    assert len(audit.measurement_plan) == 3
    assert audit.llms_txt["citation_guarantee"] is False


def test_conflicting_visibility_providers_are_not_collapsed():
    audit = audit_geo(GeoSnapshot(
        "https://example.com",
        crawler_access=(("OAI-SearchBot", "allowed"),),
        answer_first_present=True,
        visibility_measurements=(
            {"provider": "provider-a", "mention_rate": 0.4},
            {"provider": "provider-b", "mention_rate": 0.7},
        ),
    ))

    assert audit.visibility_measurements["status"] == "conflicting"
    assert set(audit.visibility_measurements["provider"]) == {"provider-a", "provider-b"}
    assert audit.visibility_measurements["data"]


def test_visibility_provider_without_data_is_unavailable():
    audit = audit_geo(GeoSnapshot(
        "https://example.com",
        crawler_access=(("OAI-SearchBot", "allowed"),),
        visibility_measurements=(),
    ))

    assert audit.visibility_measurements == {"status": "unavailable", "provider": None, "data": None}


def test_repository_proposals_require_authorization_and_never_deploy():
    denied = propose_geo_improvements(False, ({"path": "docs/faq.md"},), "org/repo")
    allowed = propose_geo_improvements(True, ({"path": "docs/faq.md"},), "org/repo")

    assert denied["status"] == "unauthorized"
    assert allowed["status"] == "proposed"
    assert allowed["repository_proposal"]["review_required"] is True
    assert allowed["merge_or_deploy_executed"] is False


def test_contracts_are_disabled_without_optional_adapters():
    result = safe_contract("neyvro_get_ai_visibility_findings", {"site": "https://example.com"})

    assert result["status"] == "disabled"
    assert result["data"] is None
    assert result["merge_or_deploy_executed"] is False
