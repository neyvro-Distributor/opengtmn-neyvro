from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import pytest

from neyvro.sequences import CampaignRuntime, CampaignSpec, CampaignState, Eligibility, SequenceStep, compile_sequence, safe_contract, schedule_compiled

NOW = datetime(2026, 10, 24, 9, tzinfo=timezone.utc)


def step(step_id="s1", channel="email"):
    return SequenceStep(step_id, channel, {"buyer_id": "b1", "company_id": "c1"}, {"mailbox_id": "m1", "identity": "sender@example.com"}, {"draft_id": "d1", "content": "approved draft"}, NOW, ("sender_available", "recipient_eligible", "approval_current"), ("reply", "unsubscribe", "hard_bounce", "meeting_booked", "customer_cancelled"), "approval-v1")


def runtime():
    spec = CampaignSpec("camp-1", "tenant-1", "approval-v1", (step(),))
    value = CampaignRuntime(spec)
    for target in (CampaignState.PROPOSED, CampaignState.PENDING_APPROVAL):
        assert value.transition(target)["status"] == "ok"
    assert value.transition(CampaignState.APPROVED, approval_version="approval-v1")["status"] == "ok"
    assert value.transition(CampaignState.SCHEDULED)["status"] == "ok"
    return value


def test_compile_is_deterministic_and_scheduler_is_injected():
    spec = CampaignSpec("camp-1", "tenant-1", "approval-v1", (step(),))
    first = compile_sequence(spec)
    second = compile_sequence(spec)
    assert first.jobs == second.jobs
    result = schedule_compiled(CampaignRuntime(spec))
    assert result["status"] == "blocked"
    scheduled = schedule_compiled(runtime(), lambda job: {"job_id": job["job_id"], "accepted": True})
    assert scheduled["status"] == "scheduled"
    assert scheduled["external_send_executed"] is False


def test_full_workflow_rechecks_eligibility_and_deduplicates_jobs():
    campaign = runtime()
    eligibility = Eligibility(True, True, True)
    first = campaign.dispatch("s1", eligibility)
    duplicate = campaign.dispatch("s1", eligibility)
    assert first["status"] == "dispatched_to_authorized_backend"
    assert duplicate["status"] == "duplicate_job"
    assert first["external_send_executed"] is False


def test_stop_events_are_idempotent_under_concurrency():
    campaign = runtime()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda event_id: campaign.handle_event("reply", event_id), ("reply-a", "reply-b")))
    assert campaign.state == CampaignState.CANCELLED
    assert sum(item["status"] == "stopped" for item in results) == 1
    assert campaign.dispatch("s1", Eligibility(True, True, True))["status"] == "blocked"


def test_revoked_approval_and_paused_campaign_cannot_dispatch():
    campaign = runtime()
    campaign.approval_version = None
    assert campaign.dispatch("s1", Eligibility(True, True, True))["reason"] == "approval version revoked or stale"
    campaign = runtime()
    assert campaign.transition(CampaignState.PAUSED)["status"] == "ok"
    assert campaign.dispatch("s1", Eligibility(True, True, True))["status"] == "blocked"


def test_unsupported_channels_and_invalid_conditions_are_rejected():
    with pytest.raises(ValueError, match="unsupported channel"):
        compile_sequence(CampaignSpec("camp", "tenant", "approval-v1", (step(channel="phone"),)))
    with pytest.raises(ValueError, match="unsupported precondition"):
        compile_sequence(CampaignSpec("camp", "tenant", "approval-v1", (SequenceStep("s1", "email", {}, {}, {}, NOW, ("run_model_code",), (), "approval-v1"),)))


def test_campaign_adapter_is_disabled_without_backend():
    result = safe_contract("neyvro_get_campaign_status", {"campaign_id": "camp-1"})
    assert result["status"] == "disabled"
    assert result["external_send_executed"] is False
