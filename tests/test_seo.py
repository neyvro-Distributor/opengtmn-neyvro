from neyvro.seo import PageSnapshot, analyze_website, propose_seo_changes, safe_contract


def page(**kwargs):
    values = dict(url="https://example.com/", title="Example", meta_description="A useful description", h1_count=1, heading_sequence=("h1", "h2"), canonical="https://example.com/", internal_links=3, image_alt_missing=0, mobile_viewport=True, https=True, structured_data_types=("Organization",), robots_allowed=True, accessible=True, source="crawl-1")
    values.update(kwargs)
    return PageSnapshot(**values)


def test_invalid_and_inaccessible_sites_fail_closed():
    assert analyze_website("not-a-url", (), authorized=True, robots_checked=True).status == "invalid_url"
    blocked = analyze_website("https://private.example", (page(accessible=False),), authorized=True, robots_checked=True)
    assert blocked.status == "inaccessible"
    assert blocked.crawl["pages_analyzed"] == 0
    assert blocked.observations[0]["observation"].startswith("Page was not analyzed")


def test_robots_must_be_checked_before_analysis():
    result = analyze_website("https://example.com", (page(),), authorized=True, robots_checked=False)
    assert result.status == "blocked"
    assert "robots directives" in result.unknown_metrics


def test_redirects_and_missing_metadata_create_actionable_issues():
    result = analyze_website("https://example.com", (page(final_url="https://www.example.com/", title=None, meta_description=None, h1_count=2, canonical=None, structured_data_types=(), image_alt_missing=2),), authorized=True, robots_checked=True)
    issue_ids = {item["issue_id"] for item in result.issues}
    assert "seo-1-redirect" in issue_ids
    assert "seo-1-title" in issue_ids
    assert "seo-1-description" in issue_ids
    assert result.recommendations[0]["priority"] in {1, 2, 3}


def test_partial_crawl_respects_rate_limits_and_does_not_invent_metrics():
    result = analyze_website("https://example.com", (page(),), authorized=True, robots_checked=True, pages_requested=10, rate_limit_events=("429 from provider",))
    assert result.status == "partial"
    assert result.crawl["robots_respected"] is True
    assert "search rankings" in result.unknown_metrics
    assert "Core Web Vitals" in result.unknown_metrics


def test_repository_changes_require_authorization_and_never_merge_or_deploy():
    denied = propose_seo_changes(False, ({"file": "index.html", "change": "add title"},), "org/site")
    assert denied["status"] == "unauthorized"
    approved = propose_seo_changes(True, ({"file": "index.html", "change": "add title"},), "org/site")
    assert approved["status"] == "proposed"
    assert approved["merge_or_deploy_executed"] is False


def test_seo_adapter_is_disabled_without_backend():
    result = safe_contract("neyvro_analyze_website", {"url": "https://example.com"})
    assert result["status"] == "disabled"
    assert result["merge_or_deploy_executed"] is False
