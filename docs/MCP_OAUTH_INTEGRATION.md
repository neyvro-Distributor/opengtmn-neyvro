# MCP OAuth integration

The gateway supports the resource-server side of standards-compliant external
OAuth: configured issuer, JWKS, resource audience, strict JWT validation and
scope checks. The protected-resource metadata is emitted by the MCP SDK only
when the external issuer/resource configuration is complete.

This repository does not implement an authorization server, consent UI,
dynamic client registration, token endpoint, refresh-token store or PKCE
authorization flow. ChatGPT, Claude, Codex and Cursor compatibility must not be
claimed until an approved OAuth provider is configured and a real
authorization-code + PKCE flow is tested.

Firebase is a first-party compatibility mode only, not an external OAuth
authorization server. Firebase and external OAuth configuration cannot be
active simultaneously.
