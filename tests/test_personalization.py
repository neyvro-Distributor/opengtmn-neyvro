from datetime import datetime, timedelta, timezone

from neyvro.personalization import MessageMaterial, PersonalizationContext, PersonalizationEvidence, generate_personalization, safe_contract, validate_outreach_claims

NOW = datetime(2026, 10, 23, tzinfo=timezone.utc)


def signal(eid="ev-1", statement="Acme is hiring platform engineers", category="hiring", roles=("VP Engineering",), verified=True):
    return PersonalizationEvidence(eid, statement, "https://example.test/evidence", NOW - timedelta(days=2), verified, category, roles)


def context(**kwargs):
    values = dict(company_id="c1", company_name="Acme", buyer_id="b1", buyer_role="VP Engineering", buyer_responsibilities=("platform reliability",), signals=(signal(),), product_benefit=MessageMaterial("Neyvro keeps evidence current.", ("positioning-v1",), False, True, "approved-positioning"), proof_point=MessageMaterial("Teams use Neyvro to organize evidence.", ("proof-1",), False, True, "approved-proof"), brand_voice="concise, practical, no hype", brand_voice_version="voice-1", positioning_version="positioning-v1")
    values.update(kwargs)
    return PersonalizationContext(**values)


def test_high_touch_output_has_reusable_evidence_linked_snippets():
    result = generate_personalization(context(), "high_touch_strategic")
    categories = {item["category"] for item in result.snippets}
    assert result.approval_status == "draft_ready"
    assert {"verified_trigger", "why_now", "relevant_pain_hypothesis", "product_benefit", "proof_point", "call_to_action"} <= categories
    assert result.snippets[0]["evidence_ids"] == ["ev-1"]
    assert result.send_allowed is False


def test_evidence_mismatch_and_buyer_role_mismatch_are_flagged():
    mismatch = validate_outreach_claims(context(), ({"category": "verified_trigger", "text": "unsupported fact", "evidence_ids": ("missing",), "generic": False},), "medium_touch_qualified")
    assert mismatch["status"] == "blocked"
    assert mismatch["flagged_claims"][0]["reason"] == "evidence_mismatch"
    wrong_role = generate_personalization(context(signals=(signal(roles=("CISO",)),)), "medium_touch_qualified")
    assert any(item["reason"] == "buyer_role_mismatch" for item in wrong_role.flagged_claims)


def test_low_information_account_stays_generic_and_labeled():
    result = generate_personalization(context(signals=(), proof_point=MessageMaterial("", (), True), product_benefit=MessageMaterial("A product benefit for teams with this problem.", (), True)), "lightweight_relevant")
    assert result.approval_status == "draft_ready"
    assert any(item["category"] == "product_benefit" and item["generic"] for item in result.snippets)
    assert any("generic product messaging" in item for item in result.confidence_limitations)
    assert not any(item["category"] == "verified_trigger" for item in result.snippets)


def test_contradictory_signals_reduce_confidence_and_block_claim():
    result = generate_personalization(context(signals=(signal("a", "Acme is hiring platform engineers"), signal("b", "Acme froze platform hiring"))), "medium_touch_qualified")
    assert result.approval_status == "needs_evidence"
    assert any(item["reason"] == "contradictory_signals" for item in result.flagged_claims)


def test_brand_voice_is_returned_and_hype_is_flagged():
    result = generate_personalization(context(product_benefit=MessageMaterial("Guaranteed revolutionary results!", (), True)), "medium_touch_qualified")
    assert result.brand_voice["version"] == "voice-1"
    assert result.brand_voice["status"] == "flagged"
    assert any(item["reason"] == "unsupported_guarantee_or_hype" for item in result.flagged_claims)


def test_personalization_adapter_is_disabled_without_backend():
    result = safe_contract("neyvro_get_brand_voice", {"workspace_id": "w1"})
    assert result["status"] == "disabled"
    assert result["send_allowed"] is False
