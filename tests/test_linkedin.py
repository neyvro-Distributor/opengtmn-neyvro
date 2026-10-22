from datetime import datetime, timedelta, timezone

from neyvro.linkedin import LinkedInEvidence, ProspectProfile, Relationship, draft_linkedin_message, get_prospect_context, record_manual_outreach, safe_contract

NOW = datetime(2026, 10, 23, tzinfo=timezone.utc)


def profile(tenant="t1", days=2, role="VP Engineering"):
    return ProspectProfile("p1", tenant, "c1", "Alex Morgan", "Example Inc", role, "https://linkedin.example/p1", NOW - timedelta(days=days), True, (LinkedInEvidence("ev-1", "the Kubernetes migration", "company-post", True, NOW - timedelta(days=days)),))


def test_connection_note_uses_verified_professional_evidence_and_manual_flow():
    result = draft_linkedin_message(profile(), "t1", "connection_note", Relationship("t1", "p1", "not_connected"), NOW)
    assert result.status == "draft_ready"
    assert result.evidence_ids == ("ev-1",)
    assert len(result.message) <= 300
    assert result.approval_status == "review_required"
    assert result.external_action_executed is False
    recorded = record_manual_outreach("t1", profile(), Relationship("t1", "p1"), "connection_note", True, NOW)
    assert recorded["status"] == "recorded"
    assert recorded["external_action_executed"] is False


def test_missing_profile_and_stale_role_are_not_guessed():
    missing = get_prospect_context(None, "t1", NOW)
    assert missing["status"] == "not_found"
    stale = draft_linkedin_message(profile(days=60), "t1", now=NOW)
    assert stale.status == "stale"
    assert stale.message == ""
    assert stale.flagged_claims[0]["reason"] == "research_gap"


def test_direct_message_requires_existing_relationship():
    result = draft_linkedin_message(profile(), "t1", "direct_message", Relationship("t1", "p1", "not_connected"), NOW)
    assert result.status == "blocked"
    assert result.flagged_claims[0]["reason"] == "direct_message_requires_connected_relationship"
    connected = draft_linkedin_message(profile(), "t1", "direct_message", Relationship("t1", "p1", "connected"), NOW)
    assert connected.status == "draft_ready"


def test_unsupported_automation_is_explicitly_not_implemented():
    result = draft_linkedin_message(profile(), "t1", "send_dm", Relationship("t1", "p1", "connected"), NOW)
    assert result.status == "unsupported"
    assert result.flagged_claims[0]["reason"] == "platform_action_not_supported"


def test_cross_tenant_records_do_not_disclose_or_write():
    assert get_prospect_context(profile("tenant-a"), "tenant-b", NOW)["status"] == "not_found"
    result = record_manual_outreach("tenant-b", profile("tenant-a"), Relationship("tenant-a", "p1"), "connection_note", True, NOW)
    assert result == {"status": "not_found", "recorded": False, "reason": "prospect is not available to this tenant"}


def test_opt_out_blocks_and_adapter_is_disabled_without_provider():
    result = draft_linkedin_message(profile(), "t1", "connection_note", Relationship("t1", "p1", "connected", opted_out=True), NOW)
    assert result.status == "blocked"
    assert result.flagged_claims[0]["reason"] == "relationship_opted_out"
    disabled = safe_contract("neyvro_get_linkedin_prospect_context", {"prospect_id": "p1"})
    assert disabled["status"] == "disabled"
    assert disabled["external_action_executed"] is False
