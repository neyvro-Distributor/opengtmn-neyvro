# Backend authentication integration

Status: **BLOCKED**.

The required trust chain is designed but not live:

`MCP OAuth principal -> short-lived audience-bound backend assertion -> Neyvro
membership/object authorization -> tenant-scoped result`

The existing backend has no endpoint that accepts this delegated MCP principal.
The current remote adapter therefore does not enable its service-token path.
It never forwards external MCP bearer tokens and never treats a caller-supplied
workspace ID as proof of membership.
