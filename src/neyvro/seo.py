"""Bounded, evidence-backed SEO analysis and proposal-only repository changes."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse
from typing import Any, Callable

CONTRACTS = ("neyvro_analyze_website", "neyvro_get_seo_recommendations", "neyvro_propose_seo_changes")


@dataclass(frozen=True)
class PageSnapshot:
    url: str
    status_code: int = 200
    final_url: str | None = None
    title: str | None = None
    meta_description: str | None = None
    h1_count: int | None = None
    heading_sequence: tuple[str, ...] = ()
    canonical: str | None = None
    internal_links: int | None = None
    image_alt_missing: int | None = None
    mobile_viewport: bool | None = None
    https: bool | None = None
    structured_data_types: tuple[str, ...] = ()
    indexable: bool | None = None
    robots_allowed: bool = True
    accessible: bool = True
    measured_latency_ms: int | None = None
    source: str = "authorized-crawl"


@dataclass(frozen=True)
class SEOIssue:
    issue_id: str
    area: str
    severity: str
    url: str
    observation: str
    evidence: tuple[str, ...]
    confidence: float


@dataclass(frozen=True)
class SEOAudit:
    status: str
    site: str
    crawl: dict[str, Any]
    observations: tuple[dict[str, Any], ...]
    issues: tuple[dict[str, Any], ...]
    recommendations: tuple[dict[str, Any], ...]
    unknown_metrics: tuple[str, ...]
    verification_checklist: tuple[str, ...]
    repository_proposal: dict[str, Any] | None
    merge_or_deploy_executed: bool = False

    def as_dict(self) -> dict[str, Any]:
        result = self.__dict__.copy()
        for field in ("observations", "issues", "recommendations", "unknown_metrics", "verification_checklist"):
            result[field] = list(result[field])
        return result


def _valid_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _issue(issue_id: str, area: str, severity: str, page: PageSnapshot, observation: str, confidence: float = 0.95) -> SEOIssue:
    return SEOIssue(issue_id, area, severity, page.url, observation, (page.source,), confidence)


def analyze_website(site: str, pages: tuple[PageSnapshot, ...] = (), *, authorized: bool = True, robots_checked: bool = False, pages_requested: int | None = None, rate_limit_events: tuple[str, ...] = ()) -> SEOAudit:
    """Analyze supplied authorized snapshots; this function performs no network access."""
    if not _valid_url(site):
        return SEOAudit("invalid_url", site, {"pages_requested": 0, "pages_analyzed": 0, "partial": False, "robots_respected": False, "rate_limit_events": []}, (), (), (), ("crawlability",), ("Provide an authorized http(s) URL.",), None)
    if not authorized:
        return SEOAudit("blocked", site, {"pages_requested": 0, "pages_analyzed": 0, "partial": False, "robots_respected": robots_checked, "rate_limit_events": list(rate_limit_events)}, (), (), (), ("authorized website access",), ("Obtain explicit website authorization before crawling.",), None)
    if not robots_checked:
        return SEOAudit("blocked", site, {"pages_requested": pages_requested or len(pages), "pages_analyzed": 0, "partial": False, "robots_respected": False, "rate_limit_events": list(rate_limit_events)}, (), (), (), ("robots directives",), ("Check robots.txt and crawl permissions before fetching pages.",), None)
    issues: list[SEOIssue] = []
    observations: list[dict[str, Any]] = []
    checklist: list[str] = []
    for index, page in enumerate(pages, 1):
        if not page.accessible or not page.robots_allowed:
            observations.append({"url": page.url, "observation": "Page was not analyzed because access or robots policy disallowed it.", "source": page.source})
            continue
        if page.final_url and page.final_url != page.url:
            observations.append({"url": page.url, "observation": f"Redirects to {page.final_url}.", "source": page.source})
            issues.append(_issue(f"seo-{index}-redirect", "crawlability", "medium", page, "Redirect target should be canonical and avoid unnecessary chains."))
        if page.status_code >= 400:
            issues.append(_issue(f"seo-{index}-status", "crawlability", "high", page, f"Observed HTTP status {page.status_code}."))
        if page.title is None or not page.title.strip():
            issues.append(_issue(f"seo-{index}-title", "metadata", "high", page, "Title tag is missing."))
        if page.meta_description is None or not page.meta_description.strip():
            issues.append(_issue(f"seo-{index}-description", "metadata", "medium", page, "Meta description is missing."))
        if page.h1_count is None:
            observations.append({"url": page.url, "observation": "Heading count unavailable.", "source": page.source})
        elif page.h1_count != 1:
            issues.append(_issue(f"seo-{index}-h1", "headings", "medium", page, f"Observed {page.h1_count} H1 elements; review hierarchy."))
        if page.internal_links == 0:
            issues.append(_issue(f"seo-{index}-links", "internal_linking", "medium", page, "No internal links were observed."))
        if page.image_alt_missing and page.image_alt_missing > 0:
            issues.append(_issue(f"seo-{index}-alt", "on_page", "low", page, f"{page.image_alt_missing} images lack observed alt text."))
        if page.mobile_viewport is False:
            issues.append(_issue(f"seo-{index}-mobile", "mobile", "high", page, "Viewport/mobile support was not observed."))
        if page.https is False:
            issues.append(_issue(f"seo-{index}-https", "technical", "high", page, "Page was observed without HTTPS."))
        if page.canonical is None:
            issues.append(_issue(f"seo-{index}-canonical", "indexing", "medium", page, "Canonical URL was not observed."))
        if not page.structured_data_types:
            issues.append(_issue(f"seo-{index}-schema", "structured_data", "low", page, "No structured-data type was observed; rich-result eligibility is unknown."))
        if page.measured_latency_ms is None:
            observations.append({"url": page.url, "observation": "Page-experience latency was not measured.", "source": page.source})
        observations.append({"url": page.url, "observation": "Authorized page snapshot analyzed.", "source": page.source})
    recommendations = tuple({"issue_id": item.issue_id, "improvement": item.observation, "priority": 1 if item.severity == "high" else 2 if item.severity == "medium" else 3, "effort": "medium", "verification": f"Re-crawl {item.url} and confirm the observed condition is resolved."} for item in issues)
    unknown = ["search rankings", "organic traffic", "click-through rate", "Core Web Vitals"]
    partial = bool(pages_requested is not None and len(pages) < pages_requested) or bool(rate_limit_events) or any(not page.accessible for page in pages)
    analyzed_count = sum(page.accessible and page.robots_allowed for page in pages)
    status = "inaccessible" if pages and analyzed_count == 0 else "partial" if partial else "complete"
    return SEOAudit(status, site, {"pages_requested": pages_requested or len(pages), "pages_analyzed": analyzed_count, "partial": partial, "robots_respected": True, "rate_limit_events": list(rate_limit_events)}, tuple(observations), tuple(item.__dict__ for item in issues), recommendations, tuple(unknown), tuple(checklist), None)


def propose_seo_changes(repository_authorized: bool, changes: tuple[dict[str, Any], ...], repository: str | None = None) -> dict[str, Any]:
    """Create a review proposal only; never merge or deploy."""
    if not repository_authorized:
        return {"status": "unauthorized", "repository_proposal": None, "merge_or_deploy_executed": False, "reason": "authorized repository access is required"}
    return {"status": "proposed", "repository_proposal": {"repository": repository, "changes": list(changes), "review_required": True}, "merge_or_deploy_executed": False}


def safe_contract(name: str, payload: dict[str, Any], transport: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None) -> dict[str, Any]:
    """Call an injected SEO adapter, otherwise remain optional and disabled."""
    if name not in CONTRACTS:
        raise ValueError(f"unknown SEO contract: {name}")
    if transport is None:
        return {"status": "disabled", "contract": name, "reason": "Neyvro SEO adapter is not configured", "data": None, "merge_or_deploy_executed": False}
    result = transport(name, payload)
    result["merge_or_deploy_executed"] = False
    return result
