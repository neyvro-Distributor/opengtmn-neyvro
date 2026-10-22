from datetime import datetime, timezone

from neyvro.deliverability import AuthenticationStatus, DeliveryMetrics, MailboxHealth, RecipientSafety, SenderLimits, audit_deliverability, safe_contract

NOW = datetime(2026, 10, 23, tzinfo=timezone.utc)


def healthy(**kwargs):
    mailbox = MailboxHealth("gmail", True, True, "sender@example.com", "example.com", NOW, "gmail")
    auth = AuthenticationStatus("verified", "verified", "verified", True, NOW, "dns-check")
    limits = SenderLimits(100, 20, 80, "steady", False, NOW, "gmail")
    metrics = DeliveryMetrics(0, 0, 1, 99, "24h", 0, NOW, "gmail")
    recipients = RecipientSafety()
    return audit_deliverability(mailbox, auth, limits, metrics, recipients)


def test_missing_dns_records_are_reported_without_inventing_placement():
    result = audit_deliverability(MailboxHealth("gmail", True, True, "sender@example.com", "example.com", NOW, "gmail"), AuthenticationStatus("missing", "unknown", "missing", True, NOW, "dns"))
    assert result.status == "blocked"
    assert result.authentication == {"spf": "missing", "dkim": "unknown", "dmarc": "missing"}
    assert not any("inbox" in item.casefold() for item in result.as_dict())


def test_disconnected_mailbox_is_blocked():
    result = audit_deliverability(MailboxHealth("microsoft", False, False, None, None, NOW, "microsoft"))
    assert result.status == "blocked"
    assert any(item["check"] == "mailbox_connection" and item["status"] == "failed" for item in result.verified_configuration_checks)


def test_exceeded_limits_and_ramp_guidance_are_explicit():
    result = audit_deliverability(MailboxHealth("gmail", True, True, "sender@example.com", "example.com", NOW, "gmail"), AuthenticationStatus("verified", "verified", "verified", True, NOW, "dns"), SenderLimits(50, 50, 0, "warming", False, NOW, "gmail"))
    assert result.status == "blocked"
    assert any("Pause sending" in item for item in result.recommendations)


def test_repeated_bounces_and_suppressed_or_unverified_recipients_block():
    result = audit_deliverability(MailboxHealth("gmail", True, True, "sender@example.com", "example.com", NOW, "gmail"), AuthenticationStatus("verified", "verified", "verified", True, NOW, "dns"), metrics=DeliveryMetrics(4, 0, 0, 96, "24h", 3, NOW, "gmail"), recipients=RecipientSafety(unverified=2, suppressed=1, repeated_bounces=3, catch_all=1, opted_out=1))
    assert result.status == "blocked"
    assert any("repeatedly bouncing" in item for item in result.recommendations)
    assert any("suppression" in item for item in result.recommendations)


def test_unauthorized_dns_is_unknown_not_failed():
    result = audit_deliverability(MailboxHealth("gmail", True, True, "sender@example.com", "example.com", NOW, "gmail"), AuthenticationStatus("verified", "verified", "verified", False, NOW, "not-authorized"))
    assert result.status == "review"
    assert result.authentication == {"spf": "unknown", "dkim": "unknown", "dmarc": "unknown"}
    assert "SPF (DNS inspection not authorized)" in result.unknown_metrics


def test_read_only_adapter_is_disabled_without_connection_and_never_allows_send():
    result = safe_contract("neyvro_get_mailbox_health", {"workspace_id": "w1"})
    assert result["status"] == "disabled"
    assert result["send_allowed"] is False
    available = safe_contract("neyvro_get_delivery_metrics", {"workspace_id": "w1"}, lambda name, payload: {"status": "available", "contract": name})
    assert available["send_allowed"] is False
