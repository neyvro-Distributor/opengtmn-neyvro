"""Neyvro-native capability discovery and approval-gated GTM workflow routing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable

CONTRACTS = ("neyvro_get_capabilities", "neyvro_get_connections", "neyvro_get_permissions", "neyvro_get_approval_status")
WORKFLOW = ("RESEARCH", "PLAN", "DRAFT", "REVIEW", "APPROVE", "EXECUTE", "VERIFY", "LEARN")

SKILL_TOOL_MAP: dict[str, tuple[str, ...]] = {
    "gtm-strategy": ("neyvro_get_customer_context", "neyvro_get_gtm_strategy", "neyvro_propose_gtm_strategy"),
    "ideal-customer-profile": ("neyvro_get_icp", "neyvro_evaluate_icp_fit", "neyvro_propose_icp_changes"),
    "positioning-and-messaging": ("neyvro_get_product_context", "neyvro_get_positioning", "neyvro_get_approved_claims", "neyvro_propose_positioning"),
    "account-research": ("neyvro_research_company", "neyvro_get_company_twin", "neyvro_get_company_signals", "neyvro_get_company_timeline", "neyvro_get_evidence"),
    "digital-twins": ("neyvro_get_company_twin", "neyvro_get_company_signals"),
    "company-changes": ("neyvro_get_company_signals", "neyvro_get_company_timeline"),
    "evidence": ("neyvro_get_evidence",),
    "negative-evidence": ("neyvro_get_evidence", "neyvro_get_negative_evidence"),
    "continuous-investigation": ("neyvro_get_investigation_status", "neyvro_get_evidence"),
    "predictive-problems": ("neyvro_get_predictive_opportunities", "neyvro_get_opportunity_signals"),
    "buying-windows": ("neyvro_get_buying_windows", "neyvro_get_opportunity_signals"),
    "buyer-matching": ("neyvro_search_buyers", "neyvro_get_opportunity_buyers"),
    "lead-sourcing-and-enrichment": ("neyvro_search_buyers", "neyvro_enrich_contact", "neyvro_get_contact_verification"),
    "discovery-and-qualification": ("neyvro_get_opportunity_qualification", "neyvro_get_buying_committee", "neyvro_get_meeting_context"),
    "outreach-personalization": ("neyvro_get_personalization_context", "neyvro_generate_personalization", "neyvro_get_brand_voice"),
    "linkedin-outreach": ("neyvro_get_linkedin_prospect_context", "neyvro_draft_linkedin_message", "neyvro_record_manual_outreach"),
    "cold-email-writing": ("neyvro_draft_email", "neyvro_check_message_claims", "neyvro_get_email_draft"),
    "email-deliverability": ("neyvro_get_mailbox_health", "neyvro_get_sender_limits", "neyvro_get_delivery_metrics", "neyvro_audit_email_configuration"),
    "multichannel-sequences": ("neyvro_create_campaign_draft", "neyvro_propose_campaign", "neyvro_get_campaign_status", "neyvro_pause_campaign"),
    "reply-handling-and-objections": ("neyvro_get_conversation", "neyvro_get_reply_status", "neyvro_classify_reply", "neyvro_get_followup_queue"),
    "content-marketing-engine": ("neyvro_generate_content_ideas", "neyvro_create_content_brief", "neyvro_draft_content", "neyvro_get_content_calendar", "neyvro_propose_social_post"),
    "seo-fundamentals": ("neyvro_analyze_website", "neyvro_get_seo_recommendations", "neyvro_propose_seo_changes"),
    "generative-engine-optimization": ("neyvro_get_geo_audit", "neyvro_get_ai_visibility_findings", "neyvro_propose_geo_improvements"),
    "outbound-metrics-and-benchmarks": ("neyvro_get_campaign_metrics", "neyvro_get_pipeline_metrics", "neyvro_get_revenue_attribution", "neyvro_get_signal_performance"),
    "company-digital-twin-analysis": ("neyvro_get_company_twin", "neyvro_get_company_timeline", "neyvro_get_company_signals", "neyvro_get_evidence"),
    "technology-change-detection": ("neyvro_get_company_twin", "neyvro_get_company_signals", "neyvro_get_company_timeline", "neyvro_get_evidence"),
    "predictive-problem-intelligence": ("neyvro_get_company_signals", "neyvro_get_predictive_opportunities", "neyvro_evaluate_icp_fit", "neyvro_get_evidence"),
    "evidence-verification": ("neyvro_get_evidence", "neyvro_get_company_timeline", "neyvro_get_company_signals"),
    "buying-window-detection": ("neyvro_get_buying_windows", "neyvro_get_company_signals", "neyvro_get_company_timeline", "neyvro_get_evidence"),
    "buyer-opportunity-matching": ("neyvro_search_buyers", "neyvro_get_opportunity_buyers", "neyvro_get_buying_committee", "neyvro_get_evidence"),
    "continuous-account-investigation": ("neyvro_get_investigation_status", "neyvro_get_company_timeline", "neyvro_get_evidence", "neyvro_research_company"),
    "negative-evidence-analysis": ("neyvro_get_negative_evidence", "neyvro_get_evidence", "neyvro_get_company_signals", "neyvro_evaluate_icp_fit"),
    "revenue-attribution": ("neyvro_get_revenue_attribution", "neyvro_get_pipeline_metrics", "neyvro_get_campaign_metrics", "neyvro_get_evidence"),
    "gtm-automation-with-chronos": ("neyvro_get_capabilities", "neyvro_get_connections", "neyvro_get_permissions", "neyvro_get_approval_status"),
    "gtm-automation-with-neyvro": ("neyvro_get_capabilities", "neyvro_get_connections", "neyvro_get_permissions", "neyvro_get_approval_status"),
}


@dataclass(frozen=True)
class WorkflowContext:
    connected: bool = False
    authenticated: bool = False
    scopes: frozenset[str] = frozenset()
    services: dict[str, str] | None = None
    connections: tuple[dict[str, Any], ...] = ()
    approvals: dict[str, str] | None = None
    tenant_id: str | None = None


def _service_status(context: WorkflowContext, tool: str) -> str:
    if not context.connected:
        return "disconnected"
    if not context.authenticated:
        return "invalid_auth"
    return (context.services or {}).get(tool, "unavailable")


def discover_capabilities(context: WorkflowContext, *, required_scopes: Iterable[str] = ()) -> dict[str, Any]:
    """Return capability state without exposing secrets or assuming undocumented services."""
    required = set(required_scopes)
    if not context.connected:
        state = "disconnected"
    elif not context.authenticated:
        state = "invalid_auth"
    elif not required.issubset(context.scopes):
        state = "insufficient_scope"
    else:
        state = "available"
    services = {}
    for skill, tools in sorted(SKILL_TOOL_MAP.items()):
        services[skill] = {tool: _service_status(context, tool) for tool in tools}
    return {
        "status": state,
        "connected": context.connected,
        "authenticated": context.authenticated,
        "granted_scopes": sorted(context.scopes),
        "required_scopes": sorted(required),
        "services": services,
        "connections": [{key: value for key, value in account.items() if key.lower() not in {"token", "secret", "password", "refresh_token"}} for account in context.connections],
        "approval_capable": bool(context.approvals is not None),
        "tenant_scope": context.tenant_id,
        "knowledge_only_available": True,
        "external_action_executed": False,
    }


def check_action(context: WorkflowContext, tool: str, *, required_scopes: Iterable[str] = (), approval_key: str | None = None, approval_required: bool = False) -> dict[str, Any]:
    """Apply server-equivalent gates before an execution adapter may be called."""
    if not context.connected:
        return {"status": "disconnected", "tool": tool, "execution_allowed": False, "knowledge_only": True, "external_action_executed": False}
    if not context.authenticated:
        return {"status": "invalid_auth", "tool": tool, "execution_allowed": False, "external_action_executed": False}
    missing = sorted(set(required_scopes) - set(context.scopes))
    if missing:
        return {"status": "insufficient_scope", "tool": tool, "missing_scopes": missing, "execution_allowed": False, "external_action_executed": False}
    service = (context.services or {}).get(tool, "unavailable")
    if service != "available":
        return {"status": service, "tool": tool, "execution_allowed": False, "external_action_executed": False}
    if approval_required:
        approval = (context.approvals or {}).get(approval_key or "")
        if approval != "approved":
            return {"status": "pending_approval", "tool": tool, "approval_key": approval_key, "execution_allowed": False, "external_action_executed": False}
    return {"status": "approved_to_execute", "tool": tool, "execution_allowed": True, "external_action_executed": False}


def coordinate_workflow(context: WorkflowContext, *, tool: str, required_scopes: Iterable[str] = (), approval_key: str | None = None, approval_required: bool = False) -> dict[str, Any]:
    gate = check_action(context, tool, required_scopes=required_scopes, approval_key=approval_key, approval_required=approval_required)
    if gate["status"] == "approved_to_execute":
        phase = "EXECUTE"
    elif gate["status"] == "pending_approval":
        phase = "APPROVE"
    elif gate.get("knowledge_only"):
        phase = "PLAN"
    else:
        phase = "RESEARCH"
    return {**gate, "workflow": list(WORKFLOW), "current_phase": phase, "next_phase": "VERIFY" if phase == "EXECUTE" else None, "draft_is_not_sent": True}


def safe_contract(name: str, payload: dict[str, Any], transport: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None) -> dict[str, Any]:
    if name not in CONTRACTS:
        raise ValueError(f"unknown Neyvro automation contract: {name}")
    if transport is None:
        return {"status": "disabled", "contract": name, "reason": "Neyvro capability adapter is not configured", "data": None, "external_action_executed": False}
    result = transport(name, payload)
    result["external_action_executed"] = False
    return result
