# Neyvro MCP E2E verification

**MCP Server:** PASS locally; public deployment BLOCKED  
**Public Endpoint:** None deployed  
**All 26 Skills:** 26/26 package-validated  
**MCP Tools:** 56 registered; local knowledge tools tested, remote customer tools not live-tested  
**OAuth Authentication:** BLOCKED for live flow; boundary checks PASS  
**Real Neyvro Backend Integration:** PARTIAL/BLOCKED  
**Codex Connection:** BLOCKED pending endpoint/OAuth  
**Codex Real Tool Invocation:** BLOCKED  
**ChatGPT Connection:** BLOCKED pending endpoint/account authorization  
**ChatGPT Real Tool Invocation:** NOT_TESTED  
**Cross-Tenant Security:** PASS at tested boundary; backend production exchange BLOCKED  
**End-to-End Business Workflow:** PARTIAL; local isolated components only  
**Critical Bugs Found:** 1 fixable registration gap found and fixed; external blockers remain  
**Critical Bugs Fixed:** 1 — added six missing target tool contracts and remote public skill surfaces  
**Final Release Decision:** NO-GO

Supporting evidence: `make verify-all` passed with 141 tests; see the other
files in this directory and `docs/verification-results.json`.
