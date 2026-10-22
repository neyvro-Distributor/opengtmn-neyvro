# Render service status

Status: **BLOCKED**.

The current Render CLI authentication expired. Exact observed results:

- `render whoami --output json`: `unauthorized`
- `render workspaces --output json`: `your token is expired; run render login`
- `render services --output json`: `your token is expired; run render login`
- Blueprint validation through Render: `401 Unauthorized`

No deployment, service creation, database modification, or unrelated-service
change was attempted. After the owner runs `render login`, the service must be
created only after confirming the correct workspace and repository.
