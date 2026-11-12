# 30-tool verification

The Render registry contains exactly 30 enabled read-only tools and 26 disabled
unsupported tools. The real runner enumerates each enabled tool from
`ADAPTER_REGISTRY`, sends it through the actual MCP protocol, and records one
result per tool. It refuses to call the gateway until both local health checks
and a real test identity token are present.

Current run: **30 blocked by unavailable prerequisites**; no tool was called.
The existing mocked boundary suite covers all 30 mappings but is reported
separately from real HTTP E2E.
# Runner status

The 30-tool runner now validates each advertised input schema, discovers
authorized fixture IDs, and uses strict `PASS_POSITIVE` classification. Tool
registration or `tools/list` visibility alone is not coverage evidence. Current
real coverage remains blocked until the gateway, AWS API, isolated database,
and genuine Firebase Token A are available in the same authorized environment.
