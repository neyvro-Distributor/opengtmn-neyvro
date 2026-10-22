from neyvro.gtm_automation import SKILL_TOOL_MAP, WorkflowContext, check_action, coordinate_workflow, discover_capabilities, safe_contract


def test_disconnected_context_keeps_knowledge_only_available():
    result = discover_capabilities(WorkflowContext(tenant_id="t1"))

    assert result["status"] == "disconnected"
    assert result["knowledge_only_available"] is True
    assert result["services"]["gtm-strategy"]["neyvro_get_gtm_strategy"] == "disconnected"
    assert result["connections"] == []


def test_invalid_auth_and_insufficient_scope_are_distinguished():
    invalid = discover_capabilities(WorkflowContext(connected=True, authenticated=False), required_scopes=("intelligence:read",))
    insufficient = discover_capabilities(WorkflowContext(connected=True, authenticated=True), required_scopes=("intelligence:read",))

    assert invalid["status"] == "invalid_auth"
    assert insufficient["status"] == "insufficient_scope"


def test_capability_discovery_redacts_account_secrets_and_reports_services():
    context = WorkflowContext(
        connected=True,
        authenticated=True,
        scopes=frozenset({"intelligence:read", "proposals:write"}),
        services={"neyvro_get_company_twin": "available", "neyvro_propose_campaign": "unavailable"},
        connections=({"provider": "gmail", "account_id": "a1", "refresh_token": "hidden"},),
        tenant_id="tenant-a",
    )

    result = discover_capabilities(context)

    assert result["services"]["digital-twins"]["neyvro_get_company_twin"] == "available"
    assert result["services"]["multichannel-sequences"]["neyvro_propose_campaign"] == "unavailable"
    assert "refresh_token" not in result["connections"][0]
    assert result["tenant_scope"] == "tenant-a"


def test_pending_approval_blocks_execution():
    context = WorkflowContext(
        connected=True,
        authenticated=True,
        scopes=frozenset({"messages:send"}),
        services={"neyvro_execute_approved_campaign": "available"},
        approvals={"campaign:v1": "pending"},
    )

    result = coordinate_workflow(context, tool="neyvro_execute_approved_campaign", required_scopes=("messages:send",), approval_key="campaign:v1", approval_required=True)

    assert result["status"] == "pending_approval"
    assert result["current_phase"] == "APPROVE"
    assert result["execution_allowed"] is False
    assert result["draft_is_not_sent"] is True


def test_approved_execution_requires_all_server_side_gates():
    context = WorkflowContext(
        connected=True,
        authenticated=True,
        scopes=frozenset({"messages:send"}),
        services={"neyvro_execute_approved_campaign": "available"},
        approvals={"campaign:v1": "approved"},
    )

    result = coordinate_workflow(context, tool="neyvro_execute_approved_campaign", required_scopes=("messages:send",), approval_key="campaign:v1", approval_required=True)

    assert result["status"] == "approved_to_execute"
    assert result["current_phase"] == "EXECUTE"
    assert result["next_phase"] == "VERIFY"
    assert result["external_action_executed"] is False


def test_skill_map_is_neyvro_native_and_covers_canonical_execution_skills():
    assert len(SKILL_TOOL_MAP) >= 26
    assert all(not tool.startswith("geo_") for tools in SKILL_TOOL_MAP.values() for tool in tools)
    assert "neyvro_get_capabilities" in SKILL_TOOL_MAP["gtm-automation-with-chronos"]


def test_discovery_contract_is_disabled_without_adapter():
    result = safe_contract("neyvro_get_capabilities", {"tenant_id": "t1"})

    assert result["status"] == "disabled"
    assert result["data"] is None
    assert result["external_action_executed"] is False
