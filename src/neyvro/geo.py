"""Evidence-labeled GEO/AEO audits without fabricated AI visibility claims."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable
from urllib.parse import urlparse

CONTRACTS = ("neyvro_get_geo_audit", "neyvro_get_ai_visibility_findings", "neyvro_propose_geo_improvements")


@dataclass(frozen=True)
class GeoObservation:
    observation_id: str
    statement: str
    source: str
    category: str
    confidence: float = 1.0


@dataclass(frozen=True)
class GeoSnapshot:
    site: str
    authorized: bool = True
    crawler_access: tuple[tuple[str, str], ...] = ()
    edge_access: tuple[tuple[str, str], ...] = ()
    server_rendered_content: bool | None = None
    noindex: bool | None = None
    nosnippet: bool | None = None
    answer_first_present: bool | None = None
    source_citations_present: bool | None = None
    schema_status: str = "unknown"
    schema_matches_visible_text: bool | None = None
    entity_names: tuple[str, ...] = ()
    entity_consistent: bool | None = None
    authority_indicators: tuple[str, ...] = ()
    llms_txt_status: str = "unknown"
    freshness_days: int | None = None
    observations: tuple[GeoObservation, ...] = ()
    visibility_measurements: tuple[dict[str, Any], ...] = ()
    missing_data: tuple[str, ...] = ()


@dataclass(frozen=True)
class GeoAudit:
    status: str
    site: str
    access_findings: tuple[dict[str, Any], ...]
    content_recommendations: tuple[dict[str, Any], ...]
    schema_findings: tuple[dict[str, Any], ...]
    entity_consistency: tuple[dict[str, Any], ...]
    authority_indicators: tuple[dict[str, Any], ...]
    freshness_findings: tuple[dict[str, Any], ...]
    llms_txt: dict[str, Any]
    visibility_measurements: dict[str, Any]
    measurement_plan: tuple[str, ...]
    conflicting_findings: tuple[str, ...]
    unknowns: tuple[str, ...]
    repository_proposal: dict[str, Any] | None
    merge_or_deploy_executed: bool = False

    def as_dict(self) -> dict[str, Any]:
        result = self.__dict__.copy()
        for field in ("access_findings", "content_recommendations", "schema_findings", "entity_consistency", "authority_indicators", "freshness_findings", "measurement_plan", "conflicting_findings", "unknowns"):
            result[field] = list(result[field])
        return result


def _valid_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _obs(snapshot: GeoSnapshot, category: str) -> list[GeoObservation]:
    return [item for item in snapshot.observations if item.category == category]


def audit_geo(snapshot: GeoSnapshot) -> GeoAudit:
    """Build a GEO audit from authorized observations only; no network access occurs."""
    if not _valid_url(snapshot.site):
        return GeoAudit("blocked", snapshot.site, (), (), (), (), (), (), {"status": "unknown", "recommendation": "none", "citation_guarantee": False}, {"status": "unavailable", "provider": None, "data": None}, (), (), ("valid authorized website URL",), None)
    if not snapshot.authorized:
        return GeoAudit("blocked", snapshot.site, (), (), (), (), (), (), {"status": "unknown", "recommendation": "none", "citation_guarantee": False}, {"status": "unavailable", "provider": None, "data": None}, (), (), ("explicit website authorization",), None)
    access: list[dict[str, Any]] = []
    conflicts: list[str] = []
    for bot, status in snapshot.crawler_access:
        access.append({"crawler": bot, "status": status, "evidence_ids": [item.observation_id for item in _obs(snapshot, "crawler_access")], "confidence": 0.95})
    edge = dict(snapshot.edge_access)
    for bot, status in snapshot.crawler_access:
        if bot in edge and edge[bot] != status:
            conflicts.append(f"crawler access conflict for {bot}: robots={status}, edge={edge[bot]}")
    if snapshot.server_rendered_content is False:
        access.append({"crawler": "rendered_content", "status": "blocked_or_limited", "recommendation": "Make important answers available in server-rendered HTML.", "confidence": 0.9})
    recommendations: list[dict[str, Any]] = []
    if snapshot.noindex is True or snapshot.nosnippet is True:
        access.append({"crawler": "index_directives", "status": "restricted", "recommendation": "Review noindex/nosnippet directives on intended public answer pages.", "confidence": 0.95})
    if snapshot.answer_first_present is False:
        recommendations.append({"recommendation": "Lead important sections with a direct, self-contained answer followed by supporting detail.", "evidence_level": "empirically_supported", "priority": 1})
    if snapshot.source_citations_present is False:
        recommendations.append({"recommendation": "Cite authoritative primary sources next to material factual claims.", "evidence_level": "empirically_supported", "priority": 1})
    if snapshot.answer_first_present is None:
        conflicts.append("answer-first content state unavailable")
    schema_findings: list[dict[str, Any]] = []
    if snapshot.schema_status == "malformed":
        schema_findings.append({"status": "malformed", "recommendation": "Repair JSON-LD syntax and validate it against visible content.", "evidence_level": "empirically_supported"})
    elif snapshot.schema_status == "missing":
        schema_findings.append({"status": "missing", "recommendation": "Add only honest schema types that describe visible content; citation lift is not guaranteed.", "evidence_level": "directional"})
    if snapshot.schema_matches_visible_text is False:
        schema_findings.append({"status": "mismatch", "recommendation": "Align structured data with visible page facts.", "evidence_level": "empirically_supported"})
    entity = []
    if snapshot.entity_consistent is False:
        entity.append({"status": "conflicting", "names": list(snapshot.entity_names), "recommendation": "Use one consistent organization/product description and canonical identity across authorized pages.", "evidence_level": "empirically_supported"})
    elif snapshot.entity_consistent is None:
        entity.append({"status": "unknown", "recommendation": "Review canonical identity, sameAs references, and descriptions across public sources.", "evidence_level": "directional"})
    authority = [{"indicator": item, "status": "observed"} for item in snapshot.authority_indicators]
    if not authority:
        authority.append({"indicator": "named authors, primary sources, and independent references", "status": "not_observed", "evidence_level": "directional"})
    freshness = []
    if snapshot.freshness_days is None:
        freshness.append({"status": "unknown", "recommendation": "Verify visible publication and modification dates without fake date bumps."})
    elif snapshot.freshness_days > 365:
        freshness.append({"status": "stale_signal", "days": snapshot.freshness_days, "recommendation": "Review whether the content is still accurate and update only substantive changes."})
    llms = {"status": snapshot.llms_txt_status, "recommendation": "Optional emerging/disputed experiment; prioritize access and useful content first.", "citation_guarantee": False}
    if snapshot.llms_txt_status == "unknown":
        llms["status"] = "unknown"
    if snapshot.visibility_measurements:
        providers = {item.get("provider") for item in snapshot.visibility_measurements}
        visibility = {"status": "conflicting" if len(providers) > 1 else "available", "provider": sorted(providers)[0] if len(providers) == 1 else sorted(str(item) for item in providers), "data": list(snapshot.visibility_measurements)}
    else:
        visibility = {"status": "unavailable", "provider": None, "data": None}
    unknowns = list(snapshot.missing_data)
    if visibility["status"] == "unavailable":
        unknowns.append("AI visibility measurements for ChatGPT, Gemini, Claude, Perplexity, and other engines")
    if not snapshot.crawler_access:
        unknowns.append("AI/search crawler access observations")
    plan = ("Build a locked set of branded and unbranded buyer prompts.", "Run each prompt repeatedly per authorized engine and record mention rate, citation rate, and cited sources.", "Compare the same prompt set before and after changes and annotate model/provider changes.")
    status = "partial" if conflicts or unknowns or visibility["status"] != "available" else "complete"
    return GeoAudit(status, snapshot.site, tuple(access), tuple(recommendations), tuple(schema_findings), tuple(entity), tuple(authority), tuple(freshness), llms, visibility, plan, tuple(dict.fromkeys(conflicts)), tuple(dict.fromkeys(unknowns)), None)


def propose_geo_improvements(repository_authorized: bool, improvements: tuple[dict[str, Any], ...], repository: str | None = None) -> dict[str, Any]:
    if not repository_authorized:
        return {"status": "unauthorized", "repository_proposal": None, "merge_or_deploy_executed": False, "reason": "authorized repository access is required"}
    return {"status": "proposed", "repository_proposal": {"repository": repository, "improvements": list(improvements), "review_required": True}, "merge_or_deploy_executed": False}


def safe_contract(name: str, payload: dict[str, Any], transport: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None) -> dict[str, Any]:
    if name not in CONTRACTS:
        raise ValueError(f"unknown GEO contract: {name}")
    if transport is None:
        return {"status": "disabled", "contract": name, "reason": "Neyvro GEO adapter is not configured", "data": None, "merge_or_deploy_executed": False}
    result = transport(name, payload)
    result["merge_or_deploy_executed"] = False
    return result
