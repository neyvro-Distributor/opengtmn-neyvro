# Customer beta readiness

Status: **NO-GO for customer-data beta; live public MCP transport is ready**.

The local knowledge workflow and public MCP transport are usable. Customer-data
beta is not authorized because OAuth/PKCE is not configured and the
MCP-to-backend tenant trust bridge is absent. The deployed health endpoint and
public skill surfaces are verified.

Required human/operator actions:

1. Provision the production OAuth authorization/resource server.
2. Implement and test the audience-bound backend identity exchange.
3. Configure the real OAuth metadata and scopes in Render.
4. Run authenticated Codex and ChatGPT tests against the live hostname.
