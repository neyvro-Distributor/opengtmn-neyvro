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
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from enum import StrEnum
from typing import Any, Callable
from urllib.parse import urlparse

import httpx
import jwt
from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from pydantic import BaseModel, ConfigDict, Field
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


class ToolMode(StrEnum):
    READ = "READ"
    RESEARCH = "RESEARCH"
    DRAFT = "DRAFT"
    PROPOSE = "PROPOSE"
    APPROVE = "APPROVE"
    EXECUTE = "EXECUTE"
    PUBLISH = "PUBLISH"


class NeyvroAccessToken(AccessToken):
    """Verified SDK token with request-scoped tenant identity."""

    tenant_id: str | None = None


class ToolRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    workspace_id: str | None = Field(default=None, min_length=1, max_length=128)
    company_id: str | None = Field(default=None, min_length=1, max_length=128)
    opportunity_id: str | None = Field(default=None, min_length=1, max_length=128)
    buyer_id: str | None = Field(default=None, min_length=1, max_length=128)
    campaign_id: str | None = Field(default=None, min_length=1, max_length=128)
    page: int = Field(default=1, ge=1, le=10000)
    page_size: int = Field(default=25, ge=1, le=MAX_PAGE_SIZE)
    approval_id: str | None = Field(default=None, min_length=1, max_length=256)
    payload: dict[str, Any] = Field(default_factory=dict)


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


def _spec(name: str, group: str, mode: ToolMode = ToolMode.READ, scopes: tuple[str, ...] = ("intelligence:read",), path: str | None = None, method: str = "GET", *, approval_required: bool = False, readiness: str = "DISABLED", required_fields: tuple[str, ...] = (), description: str = "") -> ToolSpec:
    return ToolSpec(name, group, mode, scopes, path, method, approval_required, readiness, description or f"{mode.value.title()} {group.lower()} data through Neyvro authorization gates.", required_fields)


TOOL_SPECS: tuple[ToolSpec, ...] = (
    _spec("neyvro_search_companies", "company intelligence", ToolMode.READ, path="/v1/discovery", readiness="PARTIAL"),
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
SPEC_BY_NAME = {spec.name: spec for spec in TOOL_SPECS}

# This is deliberately derived from the canonical repository once at startup.
# It is an allowlist: callers cannot turn a path, URI, or partial name into a
# filesystem read.
PUBLIC_SKILL_NAMES = frozenset(skill.name for skill in discover_skills(SKILLS_ROOT))


class BackendDisabled(Exception):
    pass


class BackendClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("NEYVRO_MCP_BACKEND_URL", "").rstrip("/")
        self.service_token = os.getenv("NEYVRO_MCP_BACKEND_SERVICE_TOKEN", "")
        self.timeout = float(os.getenv("NEYVRO_MCP_BACKEND_TIMEOUT_SECONDS", "10"))

    async def request(self, spec: ToolSpec, request: ToolRequest, tenant_id: str) -> dict[str, Any]:
        # Do not activate this path from environment presence alone. The
        # current AWS service-token + tenant-header arrangement is not a
        # delegated identity bridge and cannot authorize customer data.
        raise BackendDisabled("backend identity bridge is not deployed")


class JWTVerifier:
    def __init__(self, issuer: str, audience: str, jwks_url: str, resource_url: str) -> None:
        self.issuer, self.audience, self.jwks_url, self.resource_url = issuer, audience, jwks_url, resource_url
        self.client = jwt.PyJWKClient(jwks_url, cache_jwk_set=True, lifespan=300)

    async def verify_token(self, token: str) -> AccessToken | None:
        global _AUTH_VERIFIED
        try:
            if not token or len(token) > 16_384:
                return None
            signing_key = await __import__("asyncio").to_thread(self.client.get_signing_key_from_jwt, token)
            claims = jwt.decode(token, signing_key.key, algorithms=["RS256"], issuer=self.issuer, audience=self.audience, options={"require": ["exp", "iat", "iss", "aud", "sub"], "verify_signature": True}, leeway=5)
            tenant = claims.get("workspace_id") or claims.get("tenant_id")
            if tenant is not None and (not isinstance(tenant, str) or not tenant):
                return None
            raw_scopes = claims.get("scope", claims.get("scp", []))
            if isinstance(raw_scopes, str):
                scopes = raw_scopes.split()
            elif isinstance(raw_scopes, list) and all(isinstance(item, str) and item for item in raw_scopes):
                scopes = raw_scopes
            else:
                return None
            _AUTH_VERIFIED = True
            return NeyvroAccessToken(token=hashlib.sha256(token.encode()).hexdigest(), client_id=str(claims["sub"]), scopes=scopes, expires_at=int(claims["exp"]), resource=self.resource_url, tenant_id=tenant)
        except (jwt.PyJWTError, ValueError, TypeError, KeyError, OSError):
            return None


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


def _https_url(value: str | None, name: str) -> str | None:
    """Validate security-sensitive URLs before they reach the SDK or HTTP client."""
    if not value:
        return None
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError(f"{name} must be an HTTPS URL without embedded credentials")
    if parsed.fragment:
        raise ValueError(f"{name} must not contain a URL fragment")
    return value.rstrip("/")


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


def _auth_context(spec: ToolSpec, request: ToolRequest) -> tuple[str | None, dict[str, Any]]:
    token = get_access_token()
    # The SDK context contains only a token returned by JWTVerifier. Tenant
    # identity comes from that verified token, never from request data or a
    # process-global claims object.
    tenant = getattr(token, "tenant_id", None) if token else None
    if token is None:
        return None, {"status": "unauthorized", "error": {"code": "missing_or_invalid_oauth", "message": "A valid OAuth bearer token with a tenant claim is required."}}
    if not tenant:
        return None, {"status": "unauthorized", "error": {"code": "tenant_context_unavailable", "message": "The verified identity has no trusted workspace claim; backend authorization is not available."}}
    missing = sorted(set(spec.scopes) - set(token.scopes))
    if missing:
        return None, {"status": "insufficient_scope", "missing_scopes": missing, "error": {"code": "missing_scope", "message": "The token does not grant this tool."}}
    if request.workspace_id and request.workspace_id != tenant:
        return None, {"status": "forbidden", "error": {"code": "tenant_mismatch", "message": "The requested workspace is outside the token tenant."}}
    if not LIMITER.allow(tenant, spec.name):
        return None, {"status": "rate_limited", "error": {"code": "rate_limit_exceeded", "message": "Retry after the rate-limit window."}}
    return tenant, {}


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


async def handle_tool(spec: ToolSpec, request: ToolRequest) -> dict[str, Any]:
    tenant, failure = _auth_context(spec, request)
    if failure:
        return failure
    assert tenant is not None
    try:
        for field in spec.required_fields:
            if not getattr(request, field, None):
                return {"status": "invalid_request", "error": {"code": "missing_argument", "message": f"{field} is required"}}
        _safe_website_url(request.payload)
        if spec.approval_required and not request.approval_id:
            return {"status": "pending_approval", "error": {"code": "approval_required", "message": "The exact customer-approved action ID is required."}}
        result = await BACKEND.request(spec, request, tenant)
        LOGGER.info(json.dumps({"event": "mcp_tool", "tool": spec.name, "tenant": tenant, "status": result.get("status")}, sort_keys=True))
        return result
    except BackendDisabled as exc:
        return {"status": "disabled", "error": {"code": "capability_unavailable", "message": str(exc)}, "readiness": spec.readiness}
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
    try:
        issuer, audience, jwks, resource_url, allowed_hosts = _oauth_config()
    except ValueError as exc:
        LOGGER.error("invalid OAuth configuration: %s", exc)
        issuer = audience = jwks = resource_url = None
        allowed_hosts = []
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
    if issuer and audience and jwks and resource_url:
        verifier = JWTVerifier(issuer, audience, jwks, resource_url)
        kwargs["token_verifier"] = verifier
        kwargs["auth"] = AuthSettings(issuer_url=issuer, resource_server_url=resource_url, required_scopes=[])
    server = FastMCP(**kwargs)
    for spec in TOOL_SPECS:
        server.add_tool(_tool_handler(spec), name=spec.name, description=spec.description, structured_output=True, meta={"readiness": spec.readiness, "mode": spec.mode.value, "required_scopes": list(spec.scopes), "approval_required": spec.approval_required, "backend_path": spec.path})
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
    if oauth_error:
        authentication = "BLOCKED"
    elif _AUTH_VERIFIED:
        authentication = "VERIFIED"
    elif oauth_complete:
        authentication = "CONFIGURED"
    else:
        authentication = "BLOCKED"
    # A static gateway token plus X-Neyvro-Tenant is not an identity bridge.
    # Keep the adapter disabled until AWS deploys the delegated assertion
    # contract documented in BACKEND_AUTH_BRIDGE.md.
    notes = [
        "OAuth configuration is not proof of token verification; VERIFIED is set only after a real token passes signature, issuer, audience, expiry, subject, tenant, and scope validation.",
        "The backend adapter remains disabled until the AWS delegated identity bridge is deployed; an incoming MCP token is never forwarded.",
        "Process-local rate limits and cost controls are not sufficient for multi-instance production without a shared store.",
    ]
    if oauth_error:
        notes.insert(0, oauth_error)
    return {"authentication": authentication, "backend_service_adapter": "DISABLED", "tools": {spec.name: "DISABLED" for spec in TOOL_SPECS}, "notes": notes}


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
