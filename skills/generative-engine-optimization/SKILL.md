---
name: generative-engine-optimization
description: Activate when assessing or improving an authorized website’s discoverability, answer-first content, entity clarity, structured data, AI-crawler access, freshness, or measurement plan for AI answer engines; never promise citations or fabricate visibility.
license: MIT
metadata:
  version: 0.2.0
  maturity: playbook
  mode: research
  required_scopes: ["intelligence:read", "proposals:write"]
  related_skills: ["seo-fundamentals", "content-marketing-engine", "evidence"]
---

# Generative engine optimization (GEO / AEO)

Help customers improve the chance that authorized, useful content is retrieved, understood, and cited by AI answer engines. GEO is non-deterministic: a single prompt, model response, or checklist score is not a visibility measurement. This optional module never changes a site automatically.

## Evidence hierarchy

Label recommendations by confidence:

- **Empirically supported / high confidence:** allow relevant crawlers, remove accidental access blocks, make important content server-rendered and answer-first, cite authoritative sources, keep claims factual, and maintain entity consistency.
- **Practical but directional:** self-contained answer blocks, clear headings, useful FAQs, named authors, visible dates, and relevant structured data improve parsing and user trust; citation lift is not guaranteed.
- **Emerging or disputed:** `llms.txt`, prompt-specific rewrites, composite GEO scores, and tactics claiming direct citation lift. Recommend only as bounded experiments, never as guarantees.

## Audit workflow

1. Confirm explicit website authorization and inspect AI/search crawler access, robots directives, WAF/edge responses, noindex/nosnippet directives, canonical URLs, and server-rendered content. A crawler restriction is an observed access issue, not a reason to invent visibility loss.
2. Review answer-first content: direct answer near the top, self-contained quotable statements, primary-source citations, clear definitions, question/intent coverage, and factual grounding.
3. Review structured data and entity consistency. Malformed schema, schema/text mismatch, conflicting organization names, stale descriptions, or inconsistent `sameAs`/canonical identity become findings with evidence.
4. Review authority indicators and freshness: named experts, primary sources, transparent authorship, visible publish/modified dates, reputable third-party references, and content updates that are real—not fake date bumps.
5. Recommend `llms.txt` only as an optional, emerging/disputed experiment. It must not outrank crawl access, useful content, authoritative sources, or ordinary SEO.
6. Build a measurement plan using a locked prompt set, repeated runs per engine, mention/citation rate, source share, and baseline-vs-after comparison. If no authorized visibility provider is integrated, return measurements as unavailable.

## Required output

```json
{
  "status": "complete|partial|blocked|unknown",
  "site": "https://example.com",
  "access_findings": [],
  "content_recommendations": [{"recommendation": "...", "evidence_level": "empirically_supported|directional|emerging_or_disputed", "priority": 1}],
  "schema_findings": [],
  "entity_consistency": [],
  "authority_indicators": [],
  "freshness_findings": [],
  "llms_txt": {"status": "present|missing|unknown", "recommendation": "optional experiment", "citation_guarantee": false},
  "visibility_measurements": {"status": "available|unavailable|conflicting", "provider": null, "data": null},
  "measurement_plan": [],
  "conflicting_findings": [],
  "unknowns": [],
  "repository_proposal": null,
  "merge_or_deploy_executed": false
}
```

Do not fabricate ChatGPT, Gemini, Claude, Perplexity, AI Overview, citation, mention, rank, or share-of-voice measurements. Do not claim `llms.txt` or schema markup guarantees citation. Every observation includes source and confidence; every recommendation states its evidence level.

## MCP contracts

- `neyvro_get_geo_audit` — read an authorized GEO audit and evidence.
- `neyvro_get_ai_visibility_findings` — read provider-reported visibility findings, or return unavailable when no provider is integrated.
- `neyvro_propose_geo_improvements` — create a reviewable repository PR/proposal when repository access is explicitly authorized.

These contracts are optional and disabled without an adapter. Repository proposals never auto-merge, deploy, publish, or silently modify a website. SEO remains a separate optional module.

See also: `seo-fundamentals` for classic technical SEO, `content-marketing-engine` for content planning, and `evidence` for provenance.
