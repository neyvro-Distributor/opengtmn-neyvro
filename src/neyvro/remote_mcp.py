"""Remote Neyvro MCP service with explicit readiness and fail-closed adapters.

This service is intentionally separate from the local knowledge MCP server. It
uses the official MCP SDK's Streamable HTTP transport and never forwards an
incoming bearer token to the backend. A configured server-to-server credential
is required before an adapter can call the existing API.
"""

from __future__ import annotations

import hashlib
import ipaddress
import json
import logging
import os
import re
import sys
import time
import uuid
from dataclasses import dataclass, replace
from pathlib import Path
from enum import StrEnum
from typing import Any, Callable
from urllib.parse import urlparse

import httpx
import jwt
from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.provider import AccessToken
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from starlette.responses import JSONResponse
from starlette.routing import Route

from .skill_library import SkillValidationError, discover as discover_skills, load as load_skill

LOGGER = logging.getLogger("neyvro.remote_mcp")
MAX_PAGE_SIZE = 100
MAX_BODY_BYTES = 512 * 1024
SKILLS_ROOT = Path(__file__).resolve().parents[2] / "skills"
MAX_SKILL_BYTES = 256 * 1024
MAX_PUBLIC_SKILL_NAME_LENGTH = 128
MAX_PUBLIC_LIST_LIMIT = 100
BRIDGE_OPERATION = "companies.search"
BRIDGE_PERMISSION = "intelligence:read"
BRIDGE_DEFAULT_ISSUER = "neyvro-mcp-gateway"
BRIDGE_DEFAULT_AUDIENCE = "neyvro-mcp-exchange"
BRIDGE_DEFAULT_KID = "gw-1"
BRIDGE_LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}
SUPPORTED_MCP_SCOPES = frozenset({"intelligence:read", "mail:read"})
RESERVED_MCP_SCOPES = frozenset({"proposals:write", "research:run"})
MAX_GRANT_SECONDS = 3600


@dataclass(frozen=True)
class ScopeGrant:
    scopes: tuple[str, ...]
    expires_at: int | None = None
    revoked: bool = False

    def effective(self, now: int | None = None) -> tuple[str, ...]:
        current = int(time.time()) if now is None else now
        if self.revoked or (self.expires_at is not None and self.expires_at <= current):
            return ()
        return tuple(scope for scope in self.scopes if scope in SUPPORTED_MCP_SCOPES)


@dataclass(frozen=True)
class IdentityBinding:
    issuer: str
    subject: str
    firebase_uid: str
    expires_at: int | None = None
    revoked: bool = False

    def active_uid(self, now: int | None = None) -> str | None:
        current = int(time.time()) if now is None else now
        if self.revoked or (self.expires_at is not None and self.expires_at <= current):
            return None
        return self.firebase_uid


class ToolMode(StrEnum):
    READ = "READ"
    RESEARCH = "RESEARCH"
    DRAFT = "DRAFT"
    PROPOSE = "PROPOSE"
    APPROVE = "APPROVE"
    EXECUTE = "EXECUTE"
    PUBLISH = "PUBLISH"


class NeyvroAccessToken(AccessToken):
    """Verified identity plus authorization granted by a trusted authority."""

    tenant_id: str | None = None
    firebase_uid: str = ""
    email_verified: bool = False
    client_name: str | None = None
    auth_mode: str = "unknown"
    grant_source: str = "none"


class ToolRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    workspace_id: str | None = Field(default=None, min_length=1, max_length=128)
    company_id: str | None = Field(default=None, min_length=1, max_length=128)
    conversation_id: str | None = Field(default=None, min_length=1, max_length=128)
    opportunity_id: str | None = Field(default=None, min_length=1, max_length=128)
    buyer_id: str | None = Field(default=None, min_length=1, max_length=128)
    campaign_id: str | None = Field(default=None, min_length=1, max_length=128)
    page: int = Field(default=1, ge=1, le=10000)
    page_size: int = Field(default=25, ge=1, le=MAX_PAGE_SIZE)
    query: str | None = Field(default=None, max_length=200)
    offset: int = Field(default=0, ge=0, le=100000)
    limit: int | None = Field(default=None, ge=1, le=300)
    filter: str = Field(default="all")
    scope: str = Field(default="all")
    channel: str | None = None
    days: int = Field(default=7)
    group: str | None = None
    cursor: str | None = Field(default=None, max_length=512)
    lifecycle: str | None = None
    min_priority: int | None = Field(default=None, ge=0, le=100)
    assigned_to_me: bool | None = None
    engagement: str | None = None
    approval_id: str | None = Field(default=None, min_length=1, max_length=256)
    payload: dict[str, Any] = Field(default_factory=dict)

    @field_validator("workspace_id")
    @classmethod
    def _workspace_uuid(cls, value: str | None) -> str | None:
        if value is None:
            return value
        try:
            parsed = uuid.UUID(value)
        except ValueError as exc:
            raise ValueError("workspace_id must be a UUID") from exc
        if value != str(parsed) or value.lower() != value:
            raise ValueError("workspace_id must be a lowercase UUID")
        return value

    @field_validator("company_id", "opportunity_id", "conversation_id", "buyer_id")
    @classmethod
    def _resource_uuid(cls, value: str | None) -> str | None:
        if value is None:
            return value
        try:
            parsed = uuid.UUID(value)
        except ValueError as exc:
            raise ValueError("resource IDs must be UUIDs") from exc
        if value != str(parsed) or value.lower() != value:
            raise ValueError("resource IDs must be lowercase UUIDs")
        return value



@dataclass(frozen=True)
class ToolSpec:
    name: str
    group: str
    mode: ToolMode
    scopes: tuple[str, ...]
    path: str | None
    method: str = "GET"
    approval_required: bool = False
    readiness: str = "DISABLED"
    description: str = ""
    required_fields: tuple[str, ...] = ()
    estimated_cost: float = 0.0
    operation: str | None = None


def _spec(name: str, group: str, mode: ToolMode = ToolMode.READ, scopes: tuple[str, ...] = ("intelligence:read",), path: str | None = None, method: str = "GET", *, approval_required: bool = False, readiness: str = "DISABLED", required_fields: tuple[str, ...] = (), description: str = "", operation: str | None = None) -> ToolSpec:
    return ToolSpec(name, group, mode, scopes, path, method, approval_required, readiness, description or f"{mode.value.title()} {group.lower()} data through Neyvro authorization gates.", required_fields, operation=operation)


TOOL_SPECS: tuple[ToolSpec, ...] = (
    _spec("neyvro_search_companies", "company intelligence", ToolMode.READ, scopes=(BRIDGE_PERMISSION,), path="/v1/mcp/companies", readiness="AVAILABLE", operation=BRIDGE_OPERATION, description="Read workspace-scoped Discovery companies without starting research or spending credits."),
    _spec("neyvro_get_company_twin", "company intelligence", path="/v1/discovery/companies/{company_id}", readiness="PARTIAL", required_fields=("company_id",)),
    _spec("neyvro_get_company_timeline", "company intelligence", path="/v1/discovery/companies/{company_id}", readiness="PARTIAL", required_fields=("company_id",)),
    _spec("neyvro_get_company_signals", "company intelligence", path="/v1/discovery/companies/{company_id}", readiness="PARTIAL", required_fields=("company_id",)),
    _spec("neyvro_get_evidence", "company intelligence", path="/v1/discovery/companies/{company_id}", readiness="PARTIAL", required_fields=("company_id",)),
    _spec("neyvro_get_monitoring_status", "company intelligence", path="/v1/discovery/companies/{company_id}", readiness="PARTIAL", required_fields=("company_id",)),
    _spec("neyvro_list_opportunities", "company intelligence", path="/v1/accounts", readiness="PARTIAL"),
    _spec("neyvro_explain_opportunity", "company intelligence", path="/v1/accounts/{opportunity_id}", readiness="PARTIAL", required_fields=("opportunity_id",)),
    _spec("neyvro_get_research_questions", "company intelligence", path="/v1/accounts/objective", readiness="PARTIAL"),
    _spec("neyvro_get_opportunity_history", "predictive intelligence", path="/v1/accounts/{opportunity_id}", readiness="PARTIAL", required_fields=("opportunity_id",)),
    _spec("neyvro_get_buying_window", "predictive intelligence", path="/v1/accounts/{opportunity_id}", readiness="PARTIAL", required_fields=("opportunity_id",)),
    _spec("neyvro_get_customer_context", "gtm strategy", path="/v1/onboarding", readiness="PARTIAL"),
    _spec("neyvro_get_icp", "gtm strategy", path="/v1/onboarding", readiness="PARTIAL"),
    _spec("neyvro_evaluate_icp_fit", "gtm strategy", ToolMode.RESEARCH, path="/v1/discovery", readiness="PARTIAL"),
    _spec("neyvro_get_positioning", "gtm strategy", path="/v1/onboarding", readiness="PARTIAL"),
    _spec("neyvro_get_gtm_strategy", "gtm strategy", path="/v1/analysis", readiness="PARTIAL"),
    _spec("neyvro_search_buyers", "buyer intelligence", path="/v1/discovery", readiness="PARTIAL"),
    _spec("neyvro_get_opportunity_buyers", "buyer intelligence", path="/v1/discovery/companies/{company_id}", readiness="PARTIAL", required_fields=("company_id",)),
    _spec("neyvro_get_buyer", "buyer intelligence", path="/v1/discovery/companies/{company_id}", readiness="PARTIAL", required_fields=("company_id",)),
    _spec("neyvro_enrich_contact", "buyer intelligence", ToolMode.RESEARCH, path="/v1/discovery/companies/{company_id}/contacts", method="POST", readiness="PARTIAL", required_fields=("company_id",)),
    _spec("neyvro_get_contact_verification", "buyer intelligence", ToolMode.RESEARCH, path="/v1/discovery/companies/{company_id}/contacts", readiness="PARTIAL", required_fields=("company_id",)),
    _spec("neyvro_research_account", "personalization", ToolMode.RESEARCH, path="/v1/discovery/companies/{company_id}", readiness="PARTIAL", required_fields=("company_id",)),
    _spec("neyvro_research_buyer", "personalization", ToolMode.RESEARCH, path="/v1/discovery/companies/{company_id}/outreach-context", readiness="PARTIAL", required_fields=("company_id",)),
    _spec("neyvro_draft_email", "personalization", ToolMode.DRAFT, path="/v1/discovery/companies/{company_id}/outreach-context", readiness="PARTIAL", required_fields=("company_id",)),
    _spec("neyvro_draft_linkedin_message", "personalization", ToolMode.DRAFT, readiness="DISABLED"),
    _spec("neyvro_validate_outreach_claims", "personalization", ToolMode.RESEARCH, path="/v1/discovery/companies/{company_id}/outreach-context", readiness="PARTIAL", required_fields=("company_id",)),
    _spec("neyvro_propose_campaign", "campaigns", ToolMode.PROPOSE, scopes=("intelligence:read", "proposals:write"), path="/v1/mail/operations/{campaign_id}/sequence", method="POST", approval_required=True, readiness="PARTIAL", required_fields=("campaign_id",)),
    _spec("neyvro_create_campaign_draft", "campaigns", ToolMode.DRAFT, scopes=("intelligence:read", "proposals:write"), path="/v1/operations/drafts/{campaign_id}", method="PUT", readiness="PARTIAL", required_fields=("campaign_id",)),
    _spec("neyvro_get_campaign", "campaigns", path="/v1/mail/operations/{campaign_id}/sequence", readiness="PARTIAL", required_fields=("campaign_id",)),
    _spec("neyvro_list_campaigns", "campaigns", path="/v1/accounts", readiness="PARTIAL"),
    _spec("neyvro_get_campaign_status", "campaigns", path="/v1/mail/operations/{campaign_id}/sequence", readiness="PARTIAL", required_fields=("campaign_id",)),
    _spec("neyvro_submit_campaign_for_approval", "campaigns", ToolMode.APPROVE, scopes=("intelligence:read", "proposals:write"), path="/v1/operations/drafts/{campaign_id}/approve", method="POST", approval_required=True, readiness="PARTIAL", required_fields=("campaign_id",)),
    _spec("neyvro_pause_campaign", "campaigns", ToolMode.PROPOSE, scopes=("intelligence:read", "proposals:write"), path="/v1/mail/sequences/{campaign_id}/pause", method="POST", approval_required=True, readiness="PARTIAL", required_fields=("campaign_id",)),
    _spec("neyvro_resume_campaign", "campaigns", ToolMode.PROPOSE, scopes=("intelligence:read", "proposals:write"), path="/v1/mail/sequences/{campaign_id}/resume", method="POST", approval_required=True, readiness="PARTIAL", required_fields=("campaign_id",)),
    _spec("neyvro_cancel_campaign", "campaigns", ToolMode.PROPOSE, scopes=("intelligence:read", "proposals:write"), path="/v1/mail/sequences/{campaign_id}/cancel", method="POST", approval_required=True, readiness="PARTIAL", required_fields=("campaign_id",)),
    _spec("neyvro_list_conversations", "conversations", path="/v1/mail/companies/{company_id}/messages", readiness="PARTIAL", required_fields=("company_id",)),
    _spec("neyvro_get_conversation", "conversations", path="/v1/mail/companies/{company_id}/messages", readiness="PARTIAL", required_fields=("company_id",)),
    _spec("neyvro_get_reply_status", "conversations", path="/v1/mail/companies/{company_id}/messages", readiness="PARTIAL", required_fields=("company_id",)),
    _spec("neyvro_get_followup_queue", "conversations", path="/v1/accounts", readiness="PARTIAL"),
    _spec("neyvro_draft_reply", "conversations", ToolMode.DRAFT, path="/v1/mail/messages/{company_id}/reply-draft", readiness="PARTIAL", required_fields=("company_id",)),
    _spec("neyvro_get_capabilities", "connections", path="/v1/mail/connections", readiness="PARTIAL"),
    _spec("neyvro_get_connections", "connections", path="/v1/mail/connections", readiness="PARTIAL"),
    _spec("neyvro_get_permissions", "connections", path="/v1/mail/connections/{company_id}/permissions", readiness="PARTIAL", required_fields=("company_id",)),
    _spec("neyvro_get_sender_status", "connections", path="/v1/mail/connections", readiness="PARTIAL"),
    _spec("neyvro_get_pipeline", "pipeline", path="/v1/accounts", readiness="PARTIAL"),
    _spec("neyvro_get_qualification", "pipeline", path="/v1/accounts/{opportunity_id}", readiness="PARTIAL", required_fields=("opportunity_id",)),
    _spec("neyvro_get_revenue_attribution", "pipeline", readiness="DISABLED"),
    _spec("neyvro_get_campaign_metrics", "pipeline", path="/v1/accounts/operational-metrics", readiness="PARTIAL"),
    _spec("neyvro_analyze_website", "seo/geo", ToolMode.RESEARCH, readiness="DISABLED"),
    _spec("neyvro_get_seo_recommendations", "seo/geo", readiness="DISABLED"),
    _spec("neyvro_get_geo_recommendations", "seo/geo", readiness="DISABLED"),
    _spec("neyvro_propose_seo_changes", "seo/geo", ToolMode.PROPOSE, scopes=("intelligence:read", "proposals:write"), approval_required=True, readiness="DISABLED"),
    _spec("neyvro_generate_content_ideas", "content", ToolMode.DRAFT, readiness="DISABLED"),
    _spec("neyvro_create_content_brief", "content", ToolMode.DRAFT, readiness="DISABLED"),
    _spec("neyvro_draft_content", "content", ToolMode.DRAFT, readiness="DISABLED"),
    _spec("neyvro_propose_social_post", "content", ToolMode.PROPOSE, scopes=("intelligence:read", "proposals:write"), approval_required=True, readiness="DISABLED"),
)

# The AWS contract deliberately has fewer operations than the historical MCP
# catalog.  Keep the catalog for compatibility, but derive readiness, route,
# method, scope and operation from this explicit allowlist.  A tool is never
# callable merely because it has a legacy path in TOOL_SPECS.
CONTRACT_OPERATIONS: dict[str, dict[str, Any]] = {
    "companies.search": {"path": "/v1/mcp/companies", "scope": "intelligence:read", "params": ("query", "page", "page_size"), "required": ("workspace_id", "query", "page", "page_size", "total", "companies")},
    "companies.get": {"path": "/v1/mcp/companies/{company_id}", "scope": "intelligence:read", "params": ("company_id",), "required": ("workspace_id", "company", "story", "outreach", "monitoring", "next_best_action")},
    "companies.people": {"path": "/v1/mcp/companies/{company_id}/people", "scope": "intelligence:read", "params": ("company_id",), "required": ("workspace_id", "company_id", "company_name", "suppressed", "contacts_checked_at", "company_routes", "people")},
    "buyers.search": {"path": "/v1/mcp/buyers", "scope": "intelligence:read", "params": ("scope", "channel", "company_id", "query", "offset", "limit"), "required": ("workspace_id", "total", "offset", "limit", "buyers")},
    "signals.list": {"path": "/v1/mcp/signals", "scope": "intelligence:read", "params": ("days", "group", "scope", "query", "cursor"), "required": ("workspace_id", "window_days", "group", "scope", "query", "total", "previous_total", "companies", "groups", "signals", "next_cursor")},
    "opportunities.list": {"path": "/v1/mcp/opportunities", "scope": "intelligence:read", "params": ("lifecycle", "min_priority", "assigned_to_me", "engagement"), "required": ("workspace_id", "state", "capacity", "today", "coverage", "brief", "changes", "changes_since", "budget", "policy_note", "generated_at")},
    "opportunities.get": {"path": "/v1/mcp/opportunities/{opportunity_id}", "scope": "intelligence:read", "params": ("opportunity_id",), "required": ("workspace_id", "summary", "recommendation", "evidence", "investigations", "revisions", "since_review", "engagement", "next_action", "prediction")},
    "objective.get": {"path": "/v1/mcp/objective", "scope": "intelligence:read", "params": (), "required": ("workspace_id", "brief_version", "brief_changed", "approved", "draft")},
    "brief.get": {"path": "/v1/mcp/brief", "scope": "intelligence:read", "params": (), "required": ("workspace_id", "onboarding_step", "onboarding_completed_at", "answers_version", "company", "product", "sales", "analysis")},
    "pipeline.get": {"path": "/v1/mcp/pipeline", "scope": "intelligence:read", "params": (), "required": ("workspace_id", "metrics", "opportunities")},
    "analytics.get": {"path": "/v1/mcp/analytics", "scope": "intelligence:read", "params": (), "required": ("workspace_id", "operational", "evaluation")},
    "conversations.list": {"path": "/v1/mcp/conversations", "scope": "mail:read", "params": ("filter", "company_id", "query", "limit"), "required": ("workspace_id", "filter", "counts", "conversations")},
    "conversations.get": {"path": "/v1/mcp/conversations/{conversation_id}", "scope": "mail:read", "params": ("conversation_id",), "required": ("workspace_id", "conversation", "mailbox", "items")},
    "mail.overview": {"path": "/v1/mcp/mail/overview", "scope": "mail:read", "params": (), "required": ("workspace_id", "period_days", "mailboxes", "stats")},
}

TOOL_OPERATION_MAP: dict[str, str] = {
    "neyvro_search_companies": "companies.search",
    "neyvro_get_company_twin": "companies.get", "neyvro_get_company_timeline": "companies.get",
    "neyvro_get_company_signals": "companies.get", "neyvro_get_evidence": "companies.get", "neyvro_get_monitoring_status": "companies.get",
    "neyvro_list_opportunities": "opportunities.list", "neyvro_explain_opportunity": "opportunities.get", "neyvro_get_opportunity_history": "opportunities.get", "neyvro_get_buying_window": "opportunities.get", "neyvro_get_qualification": "opportunities.get",
    "neyvro_get_research_questions": "objective.get", "neyvro_get_customer_context": "brief.get", "neyvro_get_icp": "brief.get", "neyvro_get_positioning": "brief.get", "neyvro_get_gtm_strategy": "brief.get",
    "neyvro_search_buyers": "buyers.search", "neyvro_get_opportunity_buyers": "companies.people", "neyvro_get_buyer": "companies.people", "neyvro_get_contact_verification": "companies.people",
    "neyvro_get_pipeline": "pipeline.get", "neyvro_list_conversations": "conversations.list", "neyvro_get_conversation": "conversations.get", "neyvro_get_reply_status": "conversations.list", "neyvro_get_followup_queue": "conversations.list",
    "neyvro_get_connections": "mail.overview", "neyvro_get_capabilities": "mail.overview", "neyvro_get_permissions": "mail.overview", "neyvro_get_sender_status": "mail.overview", "neyvro_get_campaign_metrics": "mail.overview",
}

def _contract_specs(specs: tuple[ToolSpec, ...]) -> tuple[ToolSpec, ...]:
    result = []
    for spec in specs:
        operation = TOOL_OPERATION_MAP.get(spec.name)
        contract = CONTRACT_OPERATIONS.get(operation or "")
        if contract is None:
            result.append(spec)
            continue
        if spec.name == "neyvro_get_conversation":
            required = ("conversation_id",)
        elif spec.name == "neyvro_get_buyer":
            required = ("company_id", "buyer_id")
        elif operation in {"companies.get", "companies.people"} and spec.name != "neyvro_search_companies":
            required = ("company_id",)
        else:
            required = spec.required_fields
        result.append(replace(spec, operation=operation, path=contract["path"], method="GET", scopes=(contract["scope"],), required_fields=required, readiness="AVAILABLE"))
    return tuple(result)

TOOL_SPECS = _contract_specs(TOOL_SPECS)
SPEC_BY_NAME = {spec.name: spec for spec in TOOL_SPECS}

# This is deliberately derived from the canonical repository once at startup.
# It is an allowlist: callers cannot turn a path, URI, or partial name into a
# filesystem read.
PUBLIC_SKILL_NAMES = frozenset(skill.name for skill in discover_skills(SKILLS_ROOT))


class BackendDisabled(Exception):
    pass


class BridgeConfigurationError(Exception):
    pass


class BridgeHTTPError(Exception):
    def __init__(self, status_code: int, code: str, workspaces: list[dict[str, str]] | None = None) -> None:
        super().__init__(code)
        self.status_code = status_code
        self.code = code
        self.workspaces = workspaces or []


class CompanyReason(BaseModel):
    tone: str
    text: str


class Company(BaseModel):
    company_id: str
    rank: int
    name: str
    domain: str
    score: int | float
    fit: int | float
    timing: int | float
    evidence: int | float
    label: str
    verdict: str | None
    status: str
    tracked: bool
    pipeline_stage: str
    is_new: bool
    summary: str
    why_now: str
    reasons: list[CompanyReason]
    assessed_at: str


class CompanySearchResponse(BaseModel):
    workspace_id: str
    operation: str
    query: str | None
    page: int
    page_size: int
    total: int
    companies: list[Company]


class ContractResponse(BaseModel):
    """Common contract envelope; operation-specific required fields are checked below."""

    model_config = ConfigDict(extra="allow")
    workspace_id: str
    operation: str


@dataclass(frozen=True)
class ToolAdapter:
    """Allowlisted AWS adapter contract for one MCP operation."""

    tool_name: str
    operation: str
    method: str
    path: str
    scope: str
    output_model: type[BaseModel]
    side_effects: str
    credit_spending: bool
    provider_requirements: tuple[str, ...] = ()
    feature_flag: str = "NEYVRO_MCP_BRIDGE_ENABLED"
    timeout_seconds: float = 10.0
    retry_policy: str = "no retries; GET only and one exchange per invocation"


OPERATION_ADAPTERS: dict[str, ToolAdapter] = {
    operation: ToolAdapter(
        tool_name=operation,
        operation=operation,
        method="GET",
        path=contract["path"],
        scope=contract["scope"],
        output_model=CompanySearchResponse if operation == "companies.search" else ContractResponse,
        side_effects="read-only; AWS transaction is rolled back",
        credit_spending=False,
    )
    for operation, contract in CONTRACT_OPERATIONS.items()
}

ADAPTER_REGISTRY: dict[str, ToolAdapter] = {
    tool_name: replace(
        OPERATION_ADAPTERS[operation],
        operation=operation,
        tool_name=tool_name,
    )
    for tool_name, operation in TOOL_OPERATION_MAP.items()
}


class BackendClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("NEYVRO_MCP_API_BASE_URL", "").rstrip("/")
        self.gateway_private_key = os.getenv("NEYVRO_MCP_GATEWAY_PRIVATE_KEY", "").replace("\\n", "\n")
        self.gateway_kid = os.getenv("NEYVRO_MCP_GATEWAY_KEY_ID", BRIDGE_DEFAULT_KID)
        self.gateway_issuer = BRIDGE_DEFAULT_ISSUER
        self.exchange_audience = BRIDGE_DEFAULT_AUDIENCE
        self.timeout = float(os.getenv("NEYVRO_MCP_BACKEND_TIMEOUT_SECONDS", "10"))
        self.enabled = os.getenv("NEYVRO_MCP_BRIDGE_ENABLED", "false").lower() == "true"
        self.client_name = os.getenv("NEYVRO_MCP_CLIENT_NAME", "neyvro-render")
        self.allowed_api_hosts = frozenset(host.strip().lower() for host in os.getenv("NEYVRO_MCP_ALLOWED_API_HOSTS", "").split(",") if host.strip())

    def _validate_configuration(self) -> None:
        if not self.enabled:
            raise BackendDisabled("NEYVRO MCP tools are unavailable")
        if not self.base_url:
            raise BridgeConfigurationError("NEYVRO_MCP_API_BASE_URL is not configured")
        parsed = urlparse(self.base_url)
        if parsed.username or parsed.password or parsed.fragment or not parsed.hostname:
            raise BridgeConfigurationError("NEYVRO_MCP_API_BASE_URL is invalid")
        host = parsed.hostname.lower()
        if parsed.scheme != "https" and host not in BRIDGE_LOCAL_HOSTS:
            raise BridgeConfigurationError("NEYVRO_MCP_API_BASE_URL must use HTTPS")
        if host not in BRIDGE_LOCAL_HOSTS and host not in self.allowed_api_hosts:
            raise BridgeConfigurationError("NEYVRO_MCP_API_BASE_URL host is not allowlisted")
        if not self.gateway_private_key:
            raise BridgeConfigurationError("NEYVRO_MCP_GATEWAY_PRIVATE_KEY is not configured")
        if self.gateway_kid not in {"gw-1", "gw-test-1"}:
            raise BridgeConfigurationError("gateway key id is not permitted")

    def _assertion(self, identity: NeyvroAccessToken, spec: ToolSpec, request: ToolRequest) -> str:
        self._validate_configuration()
        adapter = ADAPTER_REGISTRY.get(spec.name)
        if adapter is None or spec.operation != adapter.operation or adapter.scope not in set(identity.scopes) or not identity.firebase_uid:
            raise BridgeConfigurationError("operation is not enabled")
        now = int(time.time())
        claims: dict[str, Any] = {
            "iss": self.gateway_issuer,
            "aud": self.exchange_audience,
            "sub": identity.firebase_uid,
            "email_verified": identity.email_verified,
            "op": spec.operation,
            "scope": adapter.scope,
            "iat": now,
            "exp": now + 60,
            "jti": str(uuid.uuid4()),
            "client": self.client_name,
        }
        if request.workspace_id:
            claims["workspace_id"] = request.workspace_id
        if not isinstance(self.client_name, str) or len(self.client_name) > 64 or not re.fullmatch(r"[a-z0-9._-]+", self.client_name):
            claims.pop("client", None)
        try:
            return jwt.encode(claims, self.gateway_private_key, algorithm="ES256", headers={"alg": "ES256", "typ": "gateway+jwt", "kid": self.gateway_kid})
        except (jwt.PyJWTError, TypeError, ValueError) as exc:
            raise BridgeConfigurationError("gateway signing key is unusable") from exc

    @staticmethod
    def _validate_request(spec: ToolSpec, request: ToolRequest) -> None:
        operation = spec.operation or ""
        if request.query is not None:
            max_length = 200 if operation == "conversations.list" else 120 if operation == "buyers.search" else 100
            if len(request.query) > max_length:
                raise ValueError(f"query must be at most {max_length} characters")
        if operation == "buyers.search":
            if request.scope not in {"all", "top", "other"}:
                raise ValueError("scope must be all, top, or other")
            if request.limit is None:
                request.limit = 25
        if operation == "signals.list":
            if request.days not in {7, 30, 90} or request.scope not in {"all", "tracked"}:
                raise ValueError("invalid signals filter")
        if operation == "conversations.list":
            if request.filter not in {"all", "replied", "waiting", "scheduled", "problems"}:
                raise ValueError("invalid conversation filter")
            if request.limit is None:
                request.limit = 50

    @staticmethod
    def _error_code(response: httpx.Response, default: str) -> tuple[str, list[dict[str, str]]]:
        try:
            body = response.json()
            detail = body.get("detail", {}) if isinstance(body, dict) else {}
            code = detail.get("code") if isinstance(detail, dict) else None
            workspaces = detail.get("workspaces", []) if isinstance(detail, dict) else []
            if isinstance(code, str) and isinstance(workspaces, list):
                safe = [item for item in workspaces if isinstance(item, dict) and all(isinstance(item.get(k), str) for k in ("id", "name", "role"))]
                return code, safe
        except (ValueError, TypeError):
            pass
        return default, []

    async def request(self, spec: ToolSpec, request: ToolRequest, identity: NeyvroAccessToken) -> dict[str, Any]:
        adapter = ADAPTER_REGISTRY.get(spec.name)
        if adapter is None or adapter.operation != spec.operation or adapter.path != spec.path or adapter.method != spec.method:
            raise BackendDisabled("This Neyvro tool has no supported AWS adapter")
        self._validate_request(spec, request)
        assertion = self._assertion(identity, spec, request)
        timeout = httpx.Timeout(min(self.timeout, adapter.timeout_seconds))
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=False) as client:
            exchange = await client.post(f"{self.base_url}/v1/integrations/mcp/exchange", headers={"Authorization": f"Bearer {assertion}", "Accept": "application/json"})
            if exchange.status_code != 200:
                code, workspaces = self._error_code(exchange, "bridge_exchange_failed")
                raise BridgeHTTPError(exchange.status_code, code, workspaces)
            try:
                exchanged = exchange.json()
                access_token = exchanged["access_token"]
                if exchanged.get("token_type") != "Bearer" or not isinstance(access_token, str) or not access_token:
                    raise ValueError
                if exchanged.get("operation") != adapter.operation or exchanged.get("expires_in") != 60:
                    raise ValueError
                uuid.UUID(exchanged["exchange_id"])
                workspace = exchanged["workspace"]
                workspace_id = workspace["id"]
                if not isinstance(workspace_id, str) or not isinstance(workspace.get("name"), str):
                    raise ValueError
                if not isinstance(exchanged.get("scopes"), list) or adapter.scope not in exchanged["scopes"]:
                    raise ValueError
            except (KeyError, TypeError, ValueError):
                raise BridgeHTTPError(502, "malformed_exchange_response")
            params: dict[str, Any] = {}
            for name in CONTRACT_OPERATIONS[adapter.operation]["params"]:
                value = getattr(request, name, None)
                if spec.name == "neyvro_get_followup_queue" and name == "filter":
                    value = "waiting"
                if value is not None and not (name == "query" and value == ""):
                    params[name] = value
            path = adapter.path
            for name in ("company_id", "opportunity_id", "conversation_id"):
                marker = "{" + name + "}"
                if marker in path:
                    value = getattr(request, name, None)
                    if not value:
                        raise BridgeHTTPError(422, "missing_argument")
                    path = path.replace(marker, value)
                    params.pop(name, None)
            if adapter.method != "GET":
                raise BridgeConfigurationError("unsupported adapter method")
            response = await client.get(f"{self.base_url}{path}", params=params, headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"})
            if response.status_code != 200:
                code, workspaces = self._error_code(response, "company_search_failed")
                raise BridgeHTTPError(response.status_code, code, workspaces)
            if len(response.content) > MAX_BODY_BYTES:
                raise BridgeHTTPError(502, "response_too_large")
            try:
                raw = response.json()
                result = adapter.output_model.model_validate(raw)
                required = CONTRACT_OPERATIONS[adapter.operation]["required"]
                if any(field not in raw for field in required) or raw.get("operation") not in (None, adapter.operation):
                    raise ValueError("response does not match the AWS contract")
            except (ValidationError, ValueError, TypeError):
                raise BridgeHTTPError(502, "malformed_contract_response")
            if result.workspace_id != workspace_id:
                raise BridgeHTTPError(502, "invalid_workspace_response")
            return {"status": "available", "data": result.model_dump(mode="json")}


class JWTVerifier:
    def __init__(self, issuer: str, audience: str, jwks_url: str, resource_url: str, *, identity_bindings: dict[str, IdentityBinding] | None = None) -> None:
        self.issuer, self.audience, self.jwks_url, self.resource_url = issuer, audience, jwks_url, resource_url
        self.identity_bindings = identity_bindings or {}
        self.client = jwt.PyJWKClient(jwks_url, cache_jwk_set=True, lifespan=300)

    def _firebase_uid_for_subject(self, subject: str) -> str | None:
        binding = self.identity_bindings.get(f"{self.issuer}\x00{subject}")
        return binding.active_uid() if binding else None

    async def verify_token(self, token: str) -> AccessToken | None:
        global _AUTH_VERIFIED
        try:
            if not token or len(token) > 16_384:
                return None
            signing_key = await __import__("asyncio").to_thread(self.client.get_signing_key_from_jwt, token)
            claims = jwt.decode(token, signing_key.key, algorithms=["RS256"], issuer=self.issuer, audience=self.audience, options={"require": ["exp", "iat", "iss", "aud", "sub"], "verify_signature": True}, leeway=5)
            subject = claims.get("sub")
            if not isinstance(subject, str) or not subject.strip():
                return None
            tenant = claims.get("workspace_id") or claims.get("tenant_id")
            if tenant is not None and (not isinstance(tenant, str) or not tenant.strip()):
                return None
            raw_scopes = claims.get("scope", claims.get("scp", []))
            if isinstance(raw_scopes, str):
                scopes = raw_scopes.split()
            elif isinstance(raw_scopes, list) and all(isinstance(item, str) and item for item in raw_scopes):
                scopes = raw_scopes
            elif raw_scopes in (None, []):
                scopes = []
            else:
                return None
            email_verified = claims.get("email_verified", False)
            if not isinstance(email_verified, bool):
                return None
            firebase_uid = self._firebase_uid_for_subject(subject)
            _AUTH_VERIFIED = True
            return NeyvroAccessToken(token=hashlib.sha256(token.encode()).hexdigest(), client_id=subject, scopes=list(dict.fromkeys(scopes)), expires_at=int(claims["exp"]), resource=self.resource_url, tenant_id=tenant, firebase_uid=firebase_uid or "", email_verified=email_verified, client_name=claims.get("client") if isinstance(claims.get("client"), str) else None, auth_mode="oauth", grant_source="oauth_scope_claim")
        except (jwt.PyJWTError, ValueError, TypeError, KeyError, OSError):
            return None


def _load_firebase_test_grants(project_id: str) -> dict[str, ScopeGrant]:
    """Load narrowly scoped grants for an explicitly isolated Firebase test project."""
    if os.getenv("NEYVRO_MCP_FIREBASE_TEST_MODE", "false").lower() != "true":
        return {}
    if "test" not in project_id.casefold() or not os.getenv("NEYVRO_MCP_FIREBASE_TEST_GRANTS_JSON"):
        return {}
    try:
        raw = json.loads(os.environ["NEYVRO_MCP_FIREBASE_TEST_GRANTS_JSON"])
        if not isinstance(raw, dict):
            return {}
        grants: dict[str, ScopeGrant] = {}
        now = int(time.time())
        for uid, value in raw.items():
            if not isinstance(uid, str) or not re.fullmatch(r"[\x21-\x7e]{1,128}", uid):
                continue
            if isinstance(value, list):
                scopes, expires_at, revoked = value, now + MAX_GRANT_SECONDS, False
            elif isinstance(value, dict):
                scopes, expires_at, revoked = value.get("scopes"), value.get("expires_at"), value.get("revoked", False)
            else:
                continue
            if not isinstance(scopes, list) or not all(isinstance(scope, str) and scope in SUPPORTED_MCP_SCOPES for scope in scopes):
                continue
            if expires_at is not None and (isinstance(expires_at, bool) or not isinstance(expires_at, int) or expires_at > now + MAX_GRANT_SECONDS):
                continue
            if not isinstance(revoked, bool):
                continue
            grants[uid] = ScopeGrant(tuple(dict.fromkeys(scopes)), expires_at, revoked)
        return grants
    except (json.JSONDecodeError, TypeError, ValueError, KeyError):
        return {}


class FirebaseTokenVerifier(JWTVerifier):
    """RS256 Firebase ID-token verifier with optional Admin revocation check."""

    def __init__(self, project_id: str, resource_url: str, *, admin_verifier: Callable[..., dict[str, Any]] | None = None, test_grants: dict[str, ScopeGrant] | None = None) -> None:
        self.project_id = project_id
        self.admin_verifier = admin_verifier
        self.test_grants = test_grants or {}
        super().__init__(
            f"https://securetoken.google.com/{project_id}",
            project_id,
            "https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com",
            resource_url,
        )

    async def verify_token(self, token: str) -> AccessToken | None:
        global _AUTH_VERIFIED
        _AUTH_VERIFIED = False
        verified = await super().verify_token(token)
        if verified is None:
            return None
        verified.firebase_uid = verified.client_id
        verified.auth_mode = "firebase"
        try:
            # The signature/issuer/audience checks have already succeeded in
            # the parent verifier; this only enforces Firebase's required
            # authentication timestamp on the verified claims.
            claims = jwt.decode(token, options={"verify_signature": False})
            auth_time = claims.get("auth_time")
            if auth_time is None or isinstance(auth_time, bool) or not isinstance(auth_time, (int, float)) or auth_time > time.time() + 5:
                return None
        except (jwt.PyJWTError, TypeError, ValueError):
            return None
        if self.admin_verifier is None:
            return None
        try:
            claims = await __import__("asyncio").to_thread(self.admin_verifier, token, check_revoked=True)
            if not isinstance(claims, dict) or claims.get("sub") != verified.client_id:
                return None
            # Admin verification is the authority for revocation/disabled state;
            # crypto and Firebase issuer/audience checks were already enforced.
            verified.email_verified = claims.get("email_verified") is True
            if not verified.email_verified:
                return None
        except Exception:  # fail closed on Firebase outage or revoked account
            return None
        # Firebase claims named scope/scp are deliberately ignored. Only the
        # explicit server-managed test grant map can authorize private tools.
        grant = self.test_grants.get(verified.firebase_uid)
        verified.scopes = list(grant.effective()) if grant else []
        verified.grant_source = "firebase_test_grant" if grant and verified.scopes else "none"
        _AUTH_VERIFIED = True
        return verified


class RateLimiter:
    def __init__(self, per_minute: int = 60) -> None:
        self.per_minute = per_minute
        self.calls: dict[tuple[str, str], list[float]] = {}

    def allow(self, tenant: str, tool: str) -> bool:
        now = time.monotonic()
        key = (tenant, tool)
        values = [value for value in self.calls.get(key, []) if value > now - 60]
        if len(values) >= self.per_minute:
            self.calls[key] = values
            return False
        values.append(now)
        self.calls[key] = values
        return True


BACKEND = BackendClient()
LIMITER = RateLimiter(int(os.getenv("NEYVRO_MCP_REQUESTS_PER_MINUTE", "60")))
PUBLIC_LIMITER = RateLimiter(int(os.getenv("NEYVRO_MCP_PUBLIC_REQUESTS_PER_MINUTE", "30")))
_AUTH_VERIFIED = False
_AUTH_CONFIG_ERROR: str | None = None


def _https_url(value: str | None, name: str) -> str | None:
    """Validate security-sensitive URLs before they reach the SDK or HTTP client."""
    if not value:
        return None
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError(f"{name} must be an HTTPS URL without embedded credentials")
    if parsed.fragment:
        raise ValueError(f"{name} must not contain a URL fragment")
    # Preserve the exact issuer string. Some providers include a required
    # trailing slash and JWT issuer comparison is exact.
    return value


def _oauth_config() -> tuple[str | None, str | None, str | None, str | None, list[str]]:
    """Return validated OAuth configuration without inventing production defaults."""
    issuer = os.getenv("NEYVRO_MCP_OAUTH_ISSUER")
    audience = os.getenv("NEYVRO_MCP_OAUTH_AUDIENCE")
    jwks = os.getenv("NEYVRO_MCP_OAUTH_JWKS_URL")
    resource = os.getenv("NEYVRO_MCP_RESOURCE_URL")
    allowed_hosts = [host.strip() for host in os.getenv("NEYVRO_MCP_ALLOWED_HOSTS", "").split(",") if host.strip()]
    if not all((issuer, audience, jwks, resource)):
        return issuer, audience, jwks, resource, allowed_hosts
    return _https_url(issuer, "NEYVRO_MCP_OAUTH_ISSUER"), audience.strip(), _https_url(jwks, "NEYVRO_MCP_OAUTH_JWKS_URL"), _https_url(resource, "NEYVRO_MCP_RESOURCE_URL"), allowed_hosts


def _firebase_admin_verifier() -> Callable[..., dict[str, Any]] | None:
    """Build the Admin SDK verifier only from protected service-account config."""
    credential_json = os.getenv("NEYVRO_MCP_FIREBASE_SERVICE_ACCOUNT_JSON", "")
    if not credential_json:
        return None
    try:
        import firebase_admin
        from firebase_admin import auth, credentials

        try:
            app = firebase_admin.get_app("neyvro-mcp")
        except ValueError:
            app = firebase_admin.initialize_app(credentials.Certificate(json.loads(credential_json)), name="neyvro-mcp")
        return lambda token, check_revoked=True: auth.verify_id_token(token, app=app, check_revoked=check_revoked)
    except Exception as exc:
        LOGGER.error("Firebase Admin configuration is unusable: %s", type(exc).__name__)
        return None


def _firebase_config() -> tuple[str | None, str | None, list[str]]:
    project = os.getenv("NEYVRO_MCP_FIREBASE_PROJECT_ID", "").strip() or None
    resource = os.getenv("NEYVRO_MCP_RESOURCE_URL", "").strip() or None
    if resource:
        resource = _https_url(resource, "NEYVRO_MCP_RESOURCE_URL")
    allowed_hosts = [host.strip() for host in os.getenv("NEYVRO_MCP_ALLOWED_HOSTS", "").split(",") if host.strip()]
    return project, resource, allowed_hosts


def _load_identity_bindings(issuer: str) -> dict[str, IdentityBinding]:
    """Load explicit issuer+subject bindings; email is never used for linking."""
    raw_text = os.getenv("NEYVRO_MCP_OAUTH_IDENTITY_BINDINGS_JSON", "")
    if not raw_text:
        return {}
    try:
        raw = json.loads(raw_text)
    except (json.JSONDecodeError, TypeError):
        return {}
    records = raw if isinstance(raw, list) else [dict(value, subject=key.split("\x00", 1)[-1], issuer=key.split("\x00", 1)[0]) for key, value in raw.items() if isinstance(value, dict)] if isinstance(raw, dict) else []
    bindings: dict[str, IdentityBinding] = {}
    for item in records:
        if not isinstance(item, dict) or item.get("issuer") != issuer:
            continue
        subject, firebase_uid = item.get("subject"), item.get("firebase_uid")
        expires_at, revoked = item.get("expires_at"), item.get("revoked", False)
        if not isinstance(subject, str) or not re.fullmatch(r"[\x21-\x7e]{1,128}", subject):
            continue
        if not isinstance(firebase_uid, str) or not re.fullmatch(r"[\x21-\x7e]{1,128}", firebase_uid):
            continue
        if expires_at is not None and (isinstance(expires_at, bool) or not isinstance(expires_at, int)):
            continue
        if not isinstance(revoked, bool):
            continue
        binding = IdentityBinding(issuer, subject, firebase_uid, expires_at, revoked)
        bindings[f"{issuer}\x00{subject}"] = binding
    return bindings


ENABLED_PRIVATE_TOOLS = frozenset(ADAPTER_REGISTRY)


def _evaluate_scope_grant(token: NeyvroAccessToken, spec: ToolSpec) -> dict[str, Any] | None:
    """Authorize only scopes already granted by the verified trust mode."""
    required = set(spec.scopes)
    granted = set(token.scopes) & SUPPORTED_MCP_SCOPES
    missing = sorted(required - granted)
    if missing:
        return {"status": "insufficient_scope", "missing_scopes": missing, "error": {"code": "missing_scope", "message": "The token does not grant this tool."}}
    return None


def _auth_context(spec: ToolSpec, request: ToolRequest) -> tuple[NeyvroAccessToken | None, dict[str, Any]]:
    token = get_access_token()
    # Firebase identity proves only who is calling. AWS decides workspace
    # membership, role, operation and permission during this request's exchange.
    if not isinstance(token, NeyvroAccessToken):
        return None, {"status": "unauthorized", "error": {"code": "missing_or_invalid_identity", "message": "A verified Firebase identity is required."}}
    if token.auth_mode == "oauth" and not token.firebase_uid:
        return None, {"status": "unauthorized", "error": {"code": "identity_binding_required", "message": "This OAuth identity is not linked to a NEYVRO account."}}
    if spec.name not in ENABLED_PRIVATE_TOOLS:
        return None, {"status": "disabled", "error": {"code": "operation_not_available", "message": "This Neyvro tool is not enabled."}, "readiness": "DISABLED"}
    scope_failure = _evaluate_scope_grant(token, spec)
    if scope_failure:
        return None, scope_failure
    limiter_key = token.firebase_uid or token.client_id
    if not LIMITER.allow(limiter_key, spec.name):
        return None, {"status": "rate_limited", "error": {"code": "rate_limit_exceeded", "message": "Retry after the rate-limit window."}}
    return token, {}


def _safe_website_url(payload: dict[str, Any]) -> None:
    value = payload.get("url") or payload.get("website")
    if value is None:
        return
    parsed = urlparse(str(value))
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("website URL must use http or https")
    host = parsed.hostname.lower()
    if host in {"localhost", "127.0.0.1", "::1", "0.0.0.0"}:
        raise ValueError("private or local website targets are not allowed")
    try:
        if ipaddress.ip_address(host).is_private or ipaddress.ip_address(host).is_loopback:
            raise ValueError("private or local website targets are not allowed")
    except ValueError as exc:
        if "private or local" in str(exc):
            raise


def _project_tool_result(spec: ToolSpec, request: ToolRequest, result: dict[str, Any]) -> dict[str, Any]:
    """Apply only deterministic, local projections promised by the tool matrix."""
    if result.get("status") != "available" or not isinstance(result.get("data"), dict):
        return result
    data = result["data"]
    if spec.name == "neyvro_get_buyer":
        people = data.get("people")
        if not isinstance(people, list):
            raise ValueError("companies.people response has no people list")
        selected = next((person for person in people if isinstance(person, dict) and person.get("id") == request.buyer_id), None)
        if selected is None:
            return {"status": "not_found", "error": {"code": "not_found", "message": "The requested record was not found."}}
        return {"status": "available", "data": {"workspace_id": data.get("workspace_id"), "company_id": data.get("company_id"), "person": selected}}
    return result


async def handle_tool(spec: ToolSpec, request: ToolRequest) -> dict[str, Any]:
    identity, failure = _auth_context(spec, request)
    if failure:
        return failure
    assert identity is not None
    try:
        for field in spec.required_fields:
            if not getattr(request, field, None):
                return {"status": "invalid_request", "error": {"code": "missing_argument", "message": f"{field} is required"}}
        _safe_website_url(request.payload)
        if spec.approval_required and not request.approval_id:
            return {"status": "pending_approval", "error": {"code": "approval_required", "message": "The exact customer-approved action ID is required."}}
        result = _project_tool_result(spec, request, await BACKEND.request(spec, request, identity))
        LOGGER.info(json.dumps({"event": "mcp_tool", "tool": spec.name, "status": result.get("status")}, sort_keys=True))
        return result
    except BackendDisabled as exc:
        return {"status": "disabled", "error": {"code": "capability_unavailable", "message": str(exc)}, "readiness": spec.readiness}
    except BridgeConfigurationError:
        return {"status": "disabled", "error": {"code": "bridge_unavailable", "message": "The Neyvro tools are unavailable."}, "readiness": "DISABLED"}
    except BridgeHTTPError as exc:
        if exc.code == "choose_workspace":
            return {"status": "workspace_selection_required", "error": {"code": exc.code, "message": "Select one of the available workspaces.", "workspaces": exc.workspaces}}
        messages = {
            "unknown_user": "The person does not have a Neyvro account.",
            "email_unverified": "Verify the account email before using Neyvro tools.",
            "scope_not_granted": "The required Neyvro permission was not granted.",
            "workspace_forbidden": "The selected workspace is not available.",
            "no_workspace": "No active Neyvro workspace is available.",
            "not_a_member": "Workspace membership is no longer active.",
            "user_disabled": "The Neyvro account is disabled.",
            "account_inactive": "The Neyvro workspace is inactive.",
            "rate_limited": "Neyvro rate limit reached; retry after the supplied delay.",
            "not_found": "The requested record was not found.",
            "not_ready": "This Neyvro workspace is not ready for that read.",
            "bridge_unavailable": "The Neyvro tools are unavailable.",
            "response_too_large": "The Neyvro backend returned an oversized response.",
        }
        if exc.status_code in {401, 403}:
            status = "unauthorized" if exc.status_code == 401 else "forbidden"
        elif exc.status_code == 429:
            status = "rate_limited"
        elif exc.status_code == 404:
            status = "not_found"
        elif exc.status_code == 422:
            status = "invalid_request"
        elif exc.status_code == 503 and exc.code == "bridge_unavailable":
            status = "disabled"
        else:
            status = "backend_unavailable"
        return {"status": status, "error": {"code": exc.code, "message": messages.get(exc.code, "The Neyvro backend did not authorize this request.")}}
    except (httpx.TimeoutException, httpx.HTTPError):
        return {"status": "backend_unavailable", "error": {"code": "provider_timeout_or_failure", "message": "The Neyvro backend did not complete the request."}}
    except ValueError as exc:
        return {"status": "invalid_request", "error": {"code": "invalid_request", "message": str(exc)}}


def _public_metadata(skill: Any) -> dict[str, Any]:
    return {
        "name": skill.name,
        "description": skill.description,
        "version": skill.version,
        "maturity": skill.maturity,
        "mode": skill.mode,
        "required_scopes": list(skill.required_scopes),
        "related_skills": list(skill.related_skills),
        "resource_uri": f"neyvro://skills/{skill.name}",
    }


def _allow_public_call(tool_name: str) -> dict[str, Any] | None:
    if not PUBLIC_LIMITER.allow("anonymous", tool_name):
        return {"status": "rate_limited", "error": {"code": "public_rate_limit_exceeded", "message": "Retry after the public skill rate-limit window."}}
    return None


def _validate_public_name(name: str) -> str:
    if not isinstance(name, str) or not name.strip() or len(name) > MAX_PUBLIC_SKILL_NAME_LENGTH:
        raise ValueError("name must be a non-empty skill identifier")
    normalized = name.strip()
    if normalized not in PUBLIC_SKILL_NAMES:
        raise ValueError("unknown public skill")
    return normalized


def _public_list_skills(query: str | None = None, limit: int = MAX_PUBLIC_LIST_LIMIT) -> list[dict[str, Any]]:
    """List bounded metadata from the canonical public skill allowlist."""
    limited = _allow_public_call("neyvro_list_skills")
    if limited:
        return [limited]
    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1 or limit > MAX_PUBLIC_LIST_LIMIT:
        raise ValueError(f"limit must be between 1 and {MAX_PUBLIC_LIST_LIMIT}")
    if query is not None and (not isinstance(query, str) or not query.strip() or len(query) > 256):
        raise ValueError("query must be a non-empty string of at most 256 characters when supplied")
    skills = discover_skills(SKILLS_ROOT)
    if query is not None:
        terms = query.casefold().split()
        skills = tuple(skill for skill in skills if any(term in (skill.name + " " + skill.description).casefold() for term in terms))
    return [_public_metadata(skill) for skill in skills if skill.name in PUBLIC_SKILL_NAMES][:limit]


def _public_get_skill(name: str) -> dict[str, Any]:
    """Return one canonical SKILL.md without accepting filesystem paths."""
    limited = _allow_public_call("neyvro_get_skill")
    if limited:
        return limited
    selected = _validate_public_name(name)
    skill = load_skill(selected, SKILLS_ROOT)
    content = skill.markdown
    if len(content.encode("utf-8")) > MAX_SKILL_BYTES:
        raise ValueError("skill resource exceeds the bounded resource size")
    return {**_public_metadata(skill), "content": content}


def _tool_handler(spec: ToolSpec) -> Callable[..., Any]:
    async def handler(request: ToolRequest, ctx: Context) -> dict[str, Any]:
        return await handle_tool(spec, request)

    handler.__name__ = spec.name
    handler.__doc__ = spec.description
    return handler


def build_server() -> FastMCP:
    global _AUTH_CONFIG_ERROR
    _AUTH_CONFIG_ERROR = None
    firebase_project, firebase_resource, firebase_hosts = _firebase_config()
    try:
        issuer, audience, jwks, resource_url, allowed_hosts = _oauth_config()
    except ValueError as exc:
        LOGGER.error("invalid OAuth configuration: %s", exc)
        issuer = audience = jwks = resource_url = None
        allowed_hosts = []
    external_oauth_configured = bool(issuer and audience and jwks and resource_url)
    if firebase_project and firebase_resource and external_oauth_configured:
        _AUTH_CONFIG_ERROR = "Firebase and external OAuth trust modes cannot be configured together"
        issuer = audience = jwks = resource_url = None
        verifier = None
    elif firebase_project and firebase_resource:
        # The Admin SDK is mandatory for the Firebase compatibility mode: a
        # cryptographically valid but revoked/disabled ID token is not enough.
        admin_verifier = _firebase_admin_verifier()
        if admin_verifier is not None:
            issuer, audience, jwks, resource_url = (
                f"https://securetoken.google.com/{firebase_project}",
                firebase_project,
                "https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com",
                firebase_resource,
            )
            allowed_hosts = firebase_hosts
            verifier = FirebaseTokenVerifier(firebase_project, firebase_resource, admin_verifier=admin_verifier, test_grants=_load_firebase_test_grants(firebase_project))
        else:
            issuer = audience = jwks = resource_url = None
            verifier = None
    elif issuer and audience and jwks and resource_url:
        verifier = JWTVerifier(issuer, audience, jwks, resource_url, identity_bindings=_load_identity_bindings(issuer))
    else:
        verifier = None
    allowed_origins = [origin.strip() for origin in os.getenv("NEYVRO_MCP_ALLOWED_ORIGINS", "").split(",") if origin.strip()]
    kwargs: dict[str, Any] = {
        "name": "neyvro-remote",
        "instructions": "Tenant-scoped Neyvro GTM tools with explicit authorization and readiness states.",
        "log_level": "WARNING",
        "transport_security": TransportSecuritySettings(
            allowed_hosts=allowed_hosts,
            allowed_origins=allowed_origins,
        ),
    }
    if verifier is not None and issuer and audience and resource_url:
        kwargs["token_verifier"] = verifier
        kwargs["auth"] = AuthSettings(issuer_url=issuer, resource_server_url=resource_url, required_scopes=[])
    server = FastMCP(**kwargs)
    for spec in TOOL_SPECS:
        if spec.name not in ENABLED_PRIVATE_TOOLS:
            continue
        adapter = ADAPTER_REGISTRY[spec.name]
        server.add_tool(_tool_handler(spec), name=spec.name, description=spec.description, structured_output=True, meta={"readiness": spec.readiness, "mode": spec.mode.value, "required_scopes": list(spec.scopes), "approval_required": spec.approval_required, "backend_path": spec.path, "x_mcp_operation": adapter.operation, "x_mcp_scope": adapter.scope, "x_mcp_read_only": True, "x_mcp_spends_credits": False})
    # These two tools intentionally do not call _auth_context and do not have
    # backend paths. They expose only the canonical public skill library.
    server.add_tool(_public_list_skills, name="neyvro_list_skills", description="List bounded metadata for the public Neyvro skill library.", structured_output=True, meta={"readiness": "AVAILABLE", "mode": "KNOWLEDGE", "auth": "PUBLIC", "read_only": True})
    server.add_tool(_public_get_skill, name="neyvro_get_skill", description="Retrieve one exact public Neyvro skill and its canonical SKILL.md content.", structured_output=True, meta={"readiness": "AVAILABLE", "mode": "KNOWLEDGE", "auth": "PUBLIC", "read_only": True})
    _register_public_skill_surfaces(server)
    return server


def _register_public_skill_surfaces(server: FastMCP) -> None:
    """Expose only the canonical public skill documents, never customer data."""
    try:
        skills = discover_skills(SKILLS_ROOT)
    except (OSError, SkillValidationError):
        LOGGER.exception("unable to register public skill surfaces")
        raise
    for skill in skills:
        selected = skill.name

        def make_resource(name: str) -> Callable[[], str]:
            def read_skill() -> str:
                content = load_skill(name, SKILLS_ROOT).markdown
                if len(content.encode("utf-8")) > MAX_SKILL_BYTES:
                    raise ValueError("skill resource exceeds the bounded resource size")
                return content

            return read_skill

        read_skill = make_resource(selected)
        read_skill.__name__ = f"remote_read_{selected.replace('-', '_')}"
        server.resource(
            f"neyvro://skills/{selected}",
            name=selected,
            title=selected.replace("-", " ").title(),
            description=skill.description,
            mime_type="text/markdown",
        )(read_skill)

        def make_prompt(name: str, description: str) -> Callable[[], str]:
            def workflow_prompt() -> str:
                return (
                    f"Use the public Neyvro skill '{name}'.\n\n"
                    f"Activation guidance: {description}\n\n"
                    "Load the exact skill resource. Customer-data actions still require the remote tool scopes and approvals described by the skill."
                )

            return workflow_prompt

        workflow_prompt = make_prompt(selected, skill.description)
        workflow_prompt.__name__ = f"remote_prompt_{selected.replace('-', '_')}"
        server.prompt(
            name=selected,
            title=selected.replace("-", " ").title(),
            description=skill.description,
        )(workflow_prompt)


def readiness_report() -> dict[str, Any]:
    try:
        issuer, audience, jwks, resource, _ = _oauth_config()
        oauth_complete = all((issuer, audience, jwks, resource))
        oauth_error = None
    except ValueError as exc:
        oauth_complete = False
        oauth_error = str(exc)
    firebase_project = bool(os.getenv("NEYVRO_MCP_FIREBASE_PROJECT_ID"))
    firebase_credentials = bool(os.getenv("NEYVRO_MCP_FIREBASE_SERVICE_ACCOUNT_JSON"))
    if _AUTH_CONFIG_ERROR:
        authentication = "BLOCKED"
    elif _AUTH_VERIFIED:
        authentication = "VERIFIED"
    elif firebase_project and firebase_credentials:
        authentication = "CONFIGURED"
    elif oauth_error:
        authentication = "BLOCKED"
    elif oauth_complete:
        authentication = "CONFIGURED"
    else:
        authentication = "BLOCKED"
    bridge_configured = bool(BACKEND.base_url and BACKEND.gateway_private_key)
    bridge_enabled = BACKEND.enabled and bridge_configured
    workspace_authorization = "REQUESTED_PER_CALL" if bridge_enabled else "BLOCKED"
    adapter = "READY" if bridge_enabled else "DISABLED"
    tool_states = {spec.name: ("AVAILABLE" if spec.name in ENABLED_PRIVATE_TOOLS and bridge_enabled else "DISABLED") for spec in TOOL_SPECS}
    notes = [
        "Authentication configuration is not proof of identity; VERIFIED is set only after a Firebase token passes RS256, issuer, audience, time, subject, and Admin SDK revocation checks.",
        "Workspace authorization is resolved by AWS on every exchange; Firebase claims never prove membership.",
        "The adapter is off by default and never forwards an incoming Firebase token.",
    ]
    if oauth_error:
        notes.insert(0, oauth_error)
    if _AUTH_CONFIG_ERROR:
        notes.insert(0, _AUTH_CONFIG_ERROR)
    return {
        "authentication_configuration": "BLOCKED" if _AUTH_CONFIG_ERROR else ("CONFIGURED" if (firebase_project and firebase_credentials) or oauth_complete else "BLOCKED"),
        "verified_identity": authentication,
        "workspace_authorization": workspace_authorization,
        "aws_adapter_readiness": adapter,
        "authentication": authentication,
        "customer_data_authorization": workspace_authorization,
        "backend_service_adapter": adapter,
        "tools": tool_states,
        "notes": notes,
    }


REMOTE_SERVER = build_server()
REMOTE_APP = REMOTE_SERVER.streamable_http_app()


async def _healthcheck(request: Any) -> JSONResponse:
    return JSONResponse({"status": "ok", **readiness_report()})


REMOTE_APP.routes.append(Route("/health", _healthcheck, methods=["GET"]))


def main() -> None:
    logging.basicConfig(stream=sys.stderr, level=logging.WARNING)
    REMOTE_SERVER.run(transport="streamable-http")


if __name__ == "__main__":  # pragma: no cover
    main()
