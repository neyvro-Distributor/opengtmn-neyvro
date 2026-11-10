# MCP deployment and rollback checklist

## Before staging

- [ ] Review `docs/AWS_BRIDGE_CONTRACT.md` against the AWS commit `1668dea`.
- [ ] Confirm the AWS bridge is deployed in the intended isolated environment.
- [ ] Generate a new P-256 gateway key pair; keep the private key only in Render.
- [ ] Put only the gateway public key in AWS `NEYVRO_MCP_GATEWAY_PUBLIC_KEYS`.
- [ ] Use distinct gateway and AWS signing key pairs and key ids.
- [ ] Create separate test Firebase users with verified emails.
- [ ] Seed only the isolated AWS test database with those real Firebase UIDs.
- [ ] Keep `NEYVRO_MCP_BRIDGE_ENABLED=false` during initial deployment.

## Render configuration

Required protected settings:

```text
NEYVRO_MCP_FIREBASE_PROJECT_ID
NEYVRO_MCP_FIREBASE_SERVICE_ACCOUNT_JSON
NEYVRO_MCP_GATEWAY_PRIVATE_KEY
NEYVRO_MCP_GATEWAY_KEY_ID=gw-test-1   # staging; gw-1 only after approval
NEYVRO_MCP_API_BASE_URL=https://<approved-api-host>
NEYVRO_MCP_RESOURCE_URL=https://<render-host>/mcp
NEYVRO_MCP_ALLOWED_HOSTS=<render-host>
```

Operational settings include `NEYVRO_MCP_BACKEND_TIMEOUT_SECONDS`,
`NEYVRO_MCP_REQUESTS_PER_MINUTE`, `NEYVRO_MCP_PUBLIC_REQUESTS_PER_MINUTE`,
and `NEYVRO_MCP_BRIDGE_ENABLED`. Never configure a static backend bearer token.

## Verification commands

```bash
cd /Users/ankitpandey/neyvro-mcp-render-bridge
PYTHONPATH=src python3 -m pytest -q
make verify-all
curl -fsS https://<render-host>/health | jq .
```

The health response must separately report Firebase configuration/identity,
workspace authorization, AWS adapter readiness, and per-tool availability.
Run the approved staging client flow only after health and unit tests pass.

## Go-live gate

- [ ] Two new staging accounts pass authorized and negative tests.
- [ ] Cross-tenant result isolation is verified against AWS data.
- [ ] AWS replay protection and audit assertions pass.
- [ ] No token or provider secret appears in logs or MCP results.
- [ ] Security review approves key storage and rotation.
- [ ] Owner explicitly approves enabling the bridge and merging the branch.

This branch does not authorize merge, deployment, infrastructure changes, or
production enablement.

## Rollback

1. Set `NEYVRO_MCP_BRIDGE_ENABLED=false` in Render.
2. Restart the Render service.
3. Confirm health reports the AWS adapter disabled and the private tool unavailable.
4. If a key may have leaked, remove its public key from AWS and rotate both key ids.
5. Re-run `pytest` and health checks before any later re-enable decision.
