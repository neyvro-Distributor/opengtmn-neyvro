# Customer beta readiness

Status: **NO-GO**.

The local knowledge workflow is usable. Customer-data beta is not authorized
because Render access is expired, no public HTTPS service exists, OAuth/PKCE is
not configured, and the MCP-to-backend tenant trust bridge is absent.

Required human/operator actions:

1. Run `render login` and confirm the Neyvro workspace and repository.
2. Provision the production OAuth authorization/resource server.
3. Implement and test the audience-bound backend identity exchange.
4. Deploy the validated Blueprint and record the actual Render hostname.
5. Configure the real endpoint, then run live Codex and ChatGPT tests.
