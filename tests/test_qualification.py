from neyvro.qualification import OpportunityContext, QualificationEvidence, qualify_opportunity, safe_contract


def ev(eid, dimension, statement, verified=True):
    return QualificationEvidence(eid, statement, f"https://example.test/{eid}", dimension, verified)


def test_incomplete_qualification_keeps_budget_and_timing_unknown():
    result = qualify_opportunity(OpportunityContext("opp-1", "t1", "Acme", "c1", buyer_name="Dana", buyer_role="CISO", evidence=(ev("need-1", "need", "Manual evidence work delays audits"),)), "BANT")
    assert result.status == "incomplete"
    assert result.qualification_dimensions["budget"]["status"] == "unknown"
    assert result.qualification_dimensions["timeline"]["status"] == "unknown"
    assert any("funding" in question.casefold() or "approved" in question.casefold() for question in result.recommended_discovery_questions)
    assert result.send_allowed is False


def test_bant_qualified_requires_explicit_verified_dimensions():
    context = OpportunityContext("opp-2", "t1", "Acme", "c1", buyer_name="Dana", buyer_role="CISO", buyer_is_decision_maker=True, evidence=(ev("b", "budget", "Budget approved for this initiative"), ev("a", "authority", "Dana owns the decision"), ev("n", "need", "Audit evidence is a material operational problem"), ev("t", "timeline", "Decision required before the October audit"), ev("p", "pain", "Critical audit preparation burden")))
    result = qualify_opportunity(context, "BANT")
    assert result.status == "qualified"
    assert result.pain_severity["severity"] == "high"
    assert len(result.confirmed_facts) == 5


def test_conflicting_information_requires_review():
    result = qualify_opportunity(OpportunityContext("opp-3", "t1", "MixedCo", "c1", evidence=(ev("t1", "timeline", "Decision this quarter"), ev("t2", "timeline", "No decision planned this year"))), "BANT")
    assert result.status == "needs_review"
    assert result.qualification_dimensions["timeline"]["status"] == "conflicting"
    assert result.conflicting_information


def test_nonbuyer_without_path_and_disqualified_account_are_not_qualified():
    nonbuyer = qualify_opportunity(OpportunityContext("opp-4", "t1", "UserCo", "c1", buyer_name="Sam", buyer_role="end user", buyer_is_decision_maker=False, is_nonbuyer=True), "BANT")
    assert nonbuyer.status == "nonbuyer"
    disqualified = qualify_opportunity(OpportunityContext("opp-5", "t1", "ExcludedCo", "c2", disqualifiers=("excluded industry",)), "MEDDIC")
    assert disqualified.status == "disqualified"
    assert "Exit" in disqualified.suggested_next_step


def test_meddpicc_maps_committee_and_reports_missing_crm_meeting_context():
    result = qualify_opportunity(OpportunityContext("opp-6", "t1", "EnterpriseCo", "c1", buyer_role="VP Security", stakeholder_roles=("economic buyer", "procurement", "technical evaluator"), crm_available=False, meeting_api_available=False, objections=("already have an internal tool",)), "MEDDPICC")
    assert result.status == "incomplete"
    assert len(result.buying_committee) == 3
    assert "CRM opportunity API unavailable; stage and ownership not refreshed" in result.research_gaps
    assert result.relevant_objections == ("already have an internal tool",)


def test_qualification_adapter_is_disabled_without_crm_or_meeting_backend():
    result = safe_contract("neyvro_get_meeting_context", {"opportunity_id": "opp-1"})
    assert result["status"] == "disabled"
    assert result["send_allowed"] is False
