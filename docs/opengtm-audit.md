# OpenGTM audit

Audit date: 2026-10-22 (Asia/Kolkata)

Reference: [NadavShanun-design/opengtm](https://github.com/NadavShanun-design/opengtm)

Reference commit audited: `fedfaebbfbc435c671ec6298dbe0a40a07f9b5d0`

## Repository inventory

The audited reference contains:

- 17 `skills/*/SKILL.md` files.
- `mcp/server.mjs`, a zero-dependency Node.js 18+ JSON-RPC-over-stdio server.
- `README.md`, `AGENTS.md`, `INTEGRATE.md`, `CONNECT-CHRONOS.md`, `index.json`, `llms.txt`.
- `package.json`, `install.sh`, `tools/build.mjs`, and `tools/validate-skills.mjs`.
- Claude plugin manifests at `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`.
- `LICENSE` under MIT, copyright 2026 Chronos (Geodo Inc.), plus `CREDITS.md`.

The 17 skill names are:

`account-research`, `cold-email-writing`, `content-marketing-engine`,
`discovery-and-qualification`, `email-deliverability`,
`generative-engine-optimization`, `gtm-automation-with-chronos`, `gtm-strategy`,
`ideal-customer-profile`, `lead-sourcing-and-enrichment`, `linkedin-outreach`,
`multichannel-sequences`, `outbound-metrics-and-benchmarks`,
`outreach-personalization`, `positioning-and-messaging`,
`reply-handling-and-objections`, and `seo-fundamentals`.

## What the reference actually implements

Each skill is substantive Markdown knowledge with YAML frontmatter (`name`,
`description`, `license`, and metadata). The build script generates `index.json`,
`llms.txt`, and `dist/opengtm.md` from those files.

The local MCP server exposes exactly three tools:

- `list_skills` — list skill names and descriptions.
- `get_skill` — return a complete `SKILL.md` by name.
- `search_skills` — keyword search over skill names and bodies.

It also exposes one `opengtm://skill/<name>` resource and one prompt per skill.
The server reads local Markdown and has no database, OAuth, tenant model, CRM,
mailbox, enrichment, campaign, or publishing backend.

The `gtm-automation-with-chronos` skill documents approximately 87 `geo_*`
tools and the separate `CONNECT-CHRONOS.md` describes the hosted Chronos MCP at
`https://app.chronos.ro/api/mcp`. Those tools are not implemented in this
repository. Documented tool names must therefore not be treated as local
execution capabilities.

## Validation performed

Commands run against the reference checkout at the commit above:

```text
node tools/validate-skills.mjs .
Found 17 skill directories
All 17 skills valid ✔

node tools/build.mjs
Built index.json (17 skills), llms.txt, dist/opengtm.md

node mcp/server.mjs  # initialize, tools/list, resources/list over stdio
17 resources returned; 3 tools returned; 17 prompts are registered
```

The validator checks skill directory naming, matching frontmatter names,
frontmatter presence, description length, duplicate names, and a 500-line limit.
It does not validate MCP protocol completeness, backend connectivity, OAuth,
tenant isolation, or outbound safety.

## License and reuse boundary

OpenGTM is MIT-licensed, but attribution and license notices must remain when
reusing material. Neyvro should either reference the upstream skills as an
optional dependency or copy only with a preserved MIT notice and a clear
attribution file. Neyvro branding and Chronos branding must not be conflated.
