---
name: seo-fundamentals
description: Activate when auditing an explicitly authorized website for technical SEO, crawlability, indexing, metadata, headings, internal links, content relevance, page experience, mobile readiness, or structured data; this optional module never deploys or merges changes.
license: MIT
metadata:
  version: 0.2.0
  maturity: playbook
  mode: research
  required_scopes: ["intelligence:read", "proposals:write"]
  related_skills: ["generative-engine-optimization", "content-marketing-engine", "evidence"]
---

# SEO fundamentals

Provide an actionable, source-attributed SEO audit for a customer-authorized website. Keep SEO optional so unavailable crawling, Search Console, repository, or performance data never blocks core company intelligence or GTM workflows.

## Audit workflow

1. Validate the URL and authorization scope. Accept only `http`/`https` URLs the customer authorized; do not crawl inaccessible, private, or unrelated hosts.
2. Read robots directives and provider rate limits before fetching. Respect disallowed paths, crawl budgets, redirects, authentication boundaries, and partial-crawl limits. A blocked page is an access result, not a guessed issue.
3. Inspect available HTML and headers for crawlability/indexing, title and meta description, canonical, heading hierarchy, internal links, image alt text, content relevance, mobile viewport, HTTPS, page-experience signals, and JSON-LD/structured data.
4. Separate observations from recommendations. Every issue includes URL/page source, observed value, severity, confidence, and why it matters. Missing Search Console/ranking/traffic/Core Web Vitals data remains `unknown`; never invent performance or search rankings.
5. Prioritize by impact, confidence, effort, and implementation dependency. Include a verification checklist with the evidence needed to confirm each fix.
6. If repository changes are requested, create only a reviewable proposal or pull request through authorized repository access. Never merge, deploy, edit DNS, or publish automatically.

## Audit areas

- **Technical:** robots.txt, sitemap discoverability, status codes, redirects/chains, canonical URLs, HTTPS, crawl errors, index directives, JavaScript dependency.
- **On-page:** unique title, meta description, one logical H1, H2/H3 hierarchy, descriptive URLs, internal linking, image alt text.
- **Content relevance:** search intent, topic coverage, useful/people-first content, freshness only when dates are observed, authorship and primary-source signals.
- **Experience/mobile:** viewport, responsive signals, page-weight/latency observations only when actually measured, mobile rendering, intrusive elements.
- **Structured data:** valid-looking JSON-LD presence/type and required-field gaps; do not promise rich results.

## Required output

```json
{
  "status": "complete|partial|blocked|invalid_url|inaccessible",
  "site": "https://example.com",
  "crawl": {"pages_requested": 10, "pages_analyzed": 7, "partial": true, "robots_respected": true, "rate_limit_events": []},
  "observations": [],
  "issues": [{"id": "seo-1", "area": "metadata", "severity": "high|medium|low|unknown", "url": "...", "observation": "...", "evidence": [], "confidence": 0.9}],
  "recommendations": [{"issue_id": "seo-1", "improvement": "...", "priority": 1, "effort": "low|medium|high", "verification": "..."}],
  "unknown_metrics": ["rankings", "organic traffic", "Core Web Vitals"],
  "verification_checklist": [],
  "repository_proposal": null,
  "merge_or_deploy_executed": false
}
```

## MCP contracts

- `neyvro_analyze_website` — run a bounded, authorized, robots-aware website analysis.
- `neyvro_get_seo_recommendations` — retrieve or prioritize recommendations from an audit.
- `neyvro_propose_seo_changes` — create a reviewable repository proposal/PR only when repository authorization exists.

These contracts are optional and disabled without an authorized adapter. Repository proposals require explicit repository access and review permissions; merge and deploy are unsupported. Do not require direct repository or DNS access for an audit.

See also: `generative-engine-optimization` for answer-engine discoverability and `content-marketing-engine` for content planning.
