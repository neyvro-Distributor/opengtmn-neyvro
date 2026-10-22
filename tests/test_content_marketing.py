from neyvro.content_marketing import ContentContext, create_content_brief, draft_content, generate_content_ideas, get_calendar, propose_social_post, safe_contract


def test_buyer_questions_produce_evidence_linked_ideas():
    context = ContentContext(
        product_name="TraceKit",
        buyer_questions=("How do platform teams reduce debugging time?", "What should we compare in observability tools?"),
        audience=("platform lead",),
        evidence=("sales-call-17",),
    )

    ideas = generate_content_ideas(context)

    assert [idea.idea_id for idea in ideas] == ["idea-001", "idea-002"]
    assert ideas[0].confidence == "supported"
    assert ideas[0].evidence == ("sales-call-17",)
    assert ideas[1].buyer_stage == "consideration"


def test_draft_flags_claims_when_product_context_is_incomplete():
    context = ContentContext(product_name="New Product", buyer_questions=("What is the problem?",))
    idea = generate_content_ideas(context)[0]
    brief = create_content_brief(context, idea, channels=("website_blog", "reddit"))

    draft = draft_content(context, brief, "A draft article with an unverified outcome.", channel="website_blog")

    assert draft["status"] == "needs_review"
    assert draft["state"] == "DRAFT"
    assert draft["claim_review"]["unsupported"]
    assert draft["external_action_executed"] is False


def test_supported_draft_keeps_brand_voice_and_does_not_publish():
    context = ContentContext(
        product_name="TraceKit",
        approved_claims=("fast local setup",),
        evidence=("product-doc-2",),
        brand_voice="clear and practical",
        brand_voice_version="voice-3",
    )
    idea = generate_content_ideas(context)[0]
    brief = create_content_brief(context, idea)

    draft = draft_content(context, brief, "TraceKit provides fast local setup.", channel="linkedin_assisted")

    assert draft["status"] == "drafted"
    assert draft["claim_review"]["supported"] == ["fast local setup"]
    assert draft["brand_voice"] == {"version": "voice-3", "status": "provided"}
    assert draft["state"] != "PUBLISHED"


def test_unsupported_channel_is_not_fabricated():
    context = ContentContext(product_name="TraceKit")
    idea = generate_content_ideas(context)[0]
    brief = create_content_brief(context, idea)

    result = draft_content(context, brief, "draft", channel="unsupported_forum")

    assert result["status"] == "unsupported"
    assert result["state"] == "FAILED"
    assert result["external_action_executed"] is False


def test_social_post_requires_authorization_and_approval():
    denied = propose_social_post("x", "Useful post", authorized=False, approved=True, publication_key="p1")
    pending = propose_social_post("x", "Useful post", authorized=True, approved=False, publication_key="p1")
    proposed = propose_social_post("x", "Useful post", authorized=True, approved=True, publication_key="p1")

    assert denied["status"] == "unauthorized"
    assert pending["status"] == "approval_required"
    assert proposed["status"] == "proposed"
    assert proposed["external_action_executed"] is False


def test_duplicate_calendar_and_publication_are_blocked():
    calendar = get_calendar(
        ({"publication_key": "p1", "state": "APPROVED"}, {"publication_key": "p1"}),
        publication_history=("already-published",),
    )
    duplicate = propose_social_post("reddit", "Helpful answer", authorized=True, approved=True, publication_key="already-published", existing_keys=("already-published",))

    assert calendar["status"] == "partial"
    assert calendar["items"][1]["duplicate"] is True
    assert duplicate["status"] == "duplicate"


def test_content_contract_is_disabled_without_adapter():
    result = safe_contract("neyvro_draft_content", {"brief_id": "brief-001"})

    assert result["status"] == "disabled"
    assert result["data"] is None
    assert result["external_action_executed"] is False
