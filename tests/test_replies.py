from datetime import datetime, timezone

from neyvro.replies import Conversation, Message, ReplyCategory, ReplyProcessor, draft_reply, safe_contract

NOW = datetime(2026, 10, 23, tzinfo=timezone.utc)


def conversation(tenant="t1"):
    return Conversation("conv-1", tenant, "thread-1", followup_id="followup-1")


def reply(body, tenant="t1", conversation_id="conv-1", thread_id="thread-1", message_id="msg-1", sender="buyer@example.com"):
    return Message(message_id, tenant, conversation_id, thread_id, sender, "seller@example.com", body, NOW)


def test_interested_reply_stops_followup_and_drafts_meeting_options():
    processor = ReplyProcessor()
    result = processor.process(conversation(), reply("Yes, Thursday works. Can we book a meeting?"), "t1", "webhook-1")
    assert result.category == ReplyCategory.MEETING_REQUEST.value
    assert result.followup_stop["status"] == "stopped"
    draft = draft_reply(result, ("Thursday 10:00", "Friday 14:00"))
    assert draft["status"] == "draft_ready"
    assert draft["send_allowed"] is False


def test_hard_rejection_and_unsubscribe_suppress():
    processor = ReplyProcessor()
    rejection = processor.process(conversation(), reply("No thanks, not interested."), "t1", "webhook-reject")
    assert rejection.category == ReplyCategory.NOT_INTERESTED.value
    assert rejection.suppression["status"] == "suppressed"
    unsub = processor.process(conversation(), reply("Please remove me from all emails.", message_id="msg-2"), "t1", "webhook-unsub")
    assert unsub.category == ReplyCategory.UNSUBSCRIBE.value
    assert "buyer@example.com" in processor.suppressed_recipients
    assert draft_reply(unsub)["status"] == "blocked"


def test_wrong_person_out_of_office_and_objection_actions():
    processor = ReplyProcessor()
    wrong = processor.process(conversation(), reply("I am not the right person; talk to Dana."), "t1", "webhook-wrong")
    assert wrong.category == ReplyCategory.WRONG_PERSON.value
    assert draft_reply(wrong)["body"]
    ooo = processor.process(conversation(), reply("Out of office, returning on November 2." , message_id="msg-2"), "t1", "webhook-ooo")
    assert ooo.category == ReplyCategory.OUT_OF_OFFICE.value
    objection = processor.process(conversation(), reply("We have no budget and already use another tool.", message_id="msg-3"), "t1", "webhook-objection")
    assert objection.category == ReplyCategory.OBJECTION.value
    assert "budget" not in draft_reply(objection, approved_material="We can share the approved comparison.")["body"]


def test_duplicate_webhook_is_idempotent_and_wrong_thread_is_rejected():
    processor = ReplyProcessor()
    first = processor.process(conversation(), reply("Tell me more"), "t1", "webhook-1")
    duplicate = processor.process(conversation(), reply("Tell me more", message_id="msg-2"), "t1", "webhook-1")
    assert first.status == "classified"
    assert duplicate.status == "duplicate"
    wrong_thread = processor.process(conversation(), reply("Tell me more", thread_id="other-thread", message_id="msg-3"), "t1", "webhook-2")
    assert wrong_thread.status == "wrong_thread"
    assert wrong_thread.followup_stop["status"] == "not_applied"


def test_tenant_isolation_does_not_disclose_or_stop_other_tenant():
    processor = ReplyProcessor()
    result = processor.process(conversation("tenant-a"), reply("Interested", tenant="tenant-a"), "tenant-b", "webhook-cross")
    assert result.status == "not_found"
    assert not processor.stopped_followups


def test_unknown_reply_stops_automation_and_read_draft_send_are_separate():
    processor = ReplyProcessor()
    result = processor.process(conversation(), reply("Here is an unrelated message"), "t1", "webhook-unknown")
    assert result.category == ReplyCategory.UNKNOWN.value
    assert result.followup_stop["status"] == "stopped"
    assert draft_reply(result)["send_allowed"] is False
    disabled = safe_contract("neyvro_get_conversation", {"conversation_id": "conv-1"})
    assert disabled["status"] == "disabled"
    assert disabled["send_allowed"] is False
