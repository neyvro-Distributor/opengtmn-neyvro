from neyvro.icp import CompanySignals, Evidence, ICPProfile, evaluate_icp_fit, safe_contract


PROFILE = ICPProfile(
    name="security ICP",
    industries=("financial services", "healthcare"),
    excluded_industries=("staffing",),
    geographies=("us", "eu"),
    min_employees=100,
    max_employees=5000,
    technologies=("aws",),
    excluded_technologies=("legacy-only",),
    buyer_personas=("ciso", "security engineering leader"),
    problems=("security compliance", "cloud risk"),
    triggers=("new security requirements", "cloud expansion", "engineering hiring"),
)


def evidence(*items: tuple[str, str]) -> tuple[Evidence, ...]:
    return tuple(Evidence(source=f"source-{i}", statement=statement, dimension=dimension) for i, (dimension, statement) in enumerate(items))


def test_matching_company_is_qualified_with_multiple_correlated_dimensions() -> None:
    result = evaluate_icp_fit(PROFILE, CompanySignals(
        company_id="acme", name="Acme Bank", industry="financial services", employees=1200,
        geography="US", technologies=("AWS",), buyer_roles=("CISO",),
        problems=("security compliance",), triggers=("new security requirements",),
        evidence=evidence(("industry", "regulated bank"), ("size", "1200 employees"), ("geography", "US HQ"), ("technology", "AWS cloud"), ("buyer", "CISO appointed"), ("problem", "SOC2 pressure"), ("trigger", "new requirement")),
    ))
    assert result.status == "qualified"
    assert result.tier == "A"
    assert result.score >= 80
    assert len(result.matched_dimensions) >= 2


def test_nonmatching_company_is_not_qualified() -> None:
    result = evaluate_icp_fit(PROFILE, CompanySignals(
        company_id="small", name="Small Studio", industry="design", employees=12,
        geography="US", technologies=("wordpress",), buyer_roles=("founder",),
        evidence=evidence(("industry", "design studio"), ("size", "12 employees"), ("geography", "US")),
    ))
    assert result.status == "nonmatching"
    assert result.tier == "C"


def test_incomplete_company_cannot_qualify_on_one_signal() -> None:
    result = evaluate_icp_fit(PROFILE, CompanySignals(
        company_id="unknown", name="Unknown Co", triggers=("cloud expansion",),
        evidence=evidence(("trigger", "announced cloud expansion")),
    ))
    assert result.status == "incomplete"
    assert result.tier == "C"
    assert "industry" in result.missing_dimensions


def test_disqualified_company_stays_disqualified_even_with_matching_signals() -> None:
    result = evaluate_icp_fit(PROFILE, CompanySignals(
        company_id="staffing", name="Staffing Co", industry="staffing", employees=1000,
        geography="US", technologies=("AWS",), buyer_roles=("CISO",),
        problems=("security compliance",), triggers=("new security requirements",),
        evidence=evidence(("industry", "staffing"), ("size", "1000 employees"), ("geography", "US"), ("technology", "AWS"), ("buyer", "CISO"), ("problem", "compliance"), ("trigger", "requirement")),
    ))
    assert result.status == "disqualified"
    assert result.disqualifiers


def test_backend_contract_is_disabled_without_adapter() -> None:
    result = safe_contract("neyvro_get_icp", {"workspace_id": "w1"})
    assert result["status"] == "disabled"
    assert result["data"] is None
