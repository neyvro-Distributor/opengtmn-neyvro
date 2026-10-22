from datetime import datetime, timedelta, timezone

from neyvro.cold_email import EmailDraftRequest, MessageEvidence, check_message_claims, draft_email, safe_contract

NOW = datetime(2026, 10, 23, tzinfo=timezone.utc)


def evidence(eid="ev-1", statement="Acme is hiring security engineers", verified=True, days=2, about_prospect=True):
    return MessageEvidence(eid, statement, "https://example.test/evidence", verified, NOW - timedelta(days=days), about_prospect)


def request(**kwargs):
    values = dict(opportunity_id="opp-1", buyer_id="buyer-1", customer_product="Neyvro", approved_positioning="Neyvro keeps security evidence current for review.", channel="email", tone="direct", company_name="Acme", buyer_name="Dana", buyer_role="CISO", positioning_evidence_ids=("positioning-v1",), prospect_evidence=(evidence(),))
    values.update(kwargs)
    return EmailDraftRequest(**values)


def test_trigger_first_draft_has_one_cta_and_evidence_ids():
    result = draft_email(request(framework="PAS", follow_up_count=1), now=NOW)
    assert result.approval_status == "draft_ready"
    assert result.send_allowed is False
    assert result.personalized_opener["evidence_ids"] == ["ev-1"]
    assert result.call_to_action == "Worth comparing notes?"
    assert result.body.count("?") == 1
    assert result.follow_up_variants


def test_unsupported_or_missing_evidence_is_flagged():
    result = draft_email(request(prospect_evidence=(evidence(verified=False),), positioning_evidence_ids=()), now=NOW)
    reasons = {item["reason"] for item in result.flagged_claims}
    assert result.approval_status == "needs_evidence"
    assert "evidence_not_verified" in reasons
    assert "approved_positioning_evidence_id_missing" in reasons
    assert result.personalized_opener["evidence_ids"] == []


def test_stale_evidence_and_poor_personalization_do_not_pass():
    result = draft_email(request(prospect_evidence=(evidence(days=60),)), now=NOW)
    assert result.approval_status == "needs_evidence"
    assert any(item["reason"] == "evidence_stale" for item in result.flagged_claims)
    assert result.personalized_opener["text"] == "No evidence-grounded opener is available."


def test_different_buyer_roles_get_role_specific_hypothesis():
    ciso = draft_email(request(buyer_role="CISO"), now=NOW)
    champion = draft_email(request(buyer_role="security engineering champion"), now=NOW)
    assert "CISO" in ciso.problem_hypothesis["text"]
    assert "security engineering champion" in champion.problem_hypothesis["text"]


def test_suppressed_recipient_is_blocked_and_never_sendable():
    result = draft_email(request(suppressed=True), now=NOW)
    assert result.approval_status == "blocked"
    assert result.send_allowed is False
    assert any(item["reason"] == "recipient_suppressed_or_opted_out" for item in result.flagged_claims)


def test_claim_checker_and_adapter_are_fail_closed():
    check = check_message_claims((evidence("missing", statement="unsupported claim"),), (), now=NOW)
    assert check.approval_status == "flagged"
    assert check.flagged_claims[0]["reason"] == "evidence_not_available"
    assert safe_contract("neyvro_draft_email", {"opportunity_id": "opp-1"})["send_allowed"] is False
    result = safe_contract("neyvro_get_email_draft", {"draft_id": "d1"}, lambda name, payload: {"status": "available", "contract": name})
    assert result["send_allowed"] is False
