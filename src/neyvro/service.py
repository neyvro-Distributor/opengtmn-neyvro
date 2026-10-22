from dataclasses import replace

from .models import ApprovalRequest, CompanyRecord, Evidence, Principal, Scope


class AuthorizationError(PermissionError):
    """Raised when a principal cannot perform an operation."""


class TenantStore:
    """Small in-memory store used by the local foundation and its tests."""

    def __init__(self) -> None:
        self._companies: dict[str, CompanyRecord] = {}
        self._approvals: dict[str, ApprovalRequest] = {}

    def add_company(self, principal: Principal, company_id: str, name: str) -> CompanyRecord:
        self._require(principal, Scope.WRITE_PROPOSALS)
        record = CompanyRecord(company_id, principal.tenant_id, name)
        self._companies[company_id] = record
        return record

    def add_evidence(self, principal: Principal, company_id: str, evidence: Evidence) -> CompanyRecord:
        self._require(principal, Scope.WRITE_PROPOSALS)
        record = self._company_for(principal, company_id)
        record.evidence.append(evidence)
        return record

    def get_company(self, principal: Principal, company_id: str) -> CompanyRecord:
        self._require(principal, Scope.READ_INTELLIGENCE)
        return self._company_for(principal, company_id)

    def propose_action(self, principal: Principal, action: str, payload: dict[str, str]) -> ApprovalRequest:
        self._require(principal, Scope.WRITE_PROPOSALS)
        request = ApprovalRequest.create(principal.tenant_id, action, payload)
        self._approvals[request.request_id] = request
        return request

    def approve_action(self, principal: Principal, request_id: str) -> ApprovalRequest:
        self._require(principal, Scope.SEND_MESSAGES)
        request = self._approvals.get(request_id)
        if request is None or request.tenant_id != principal.tenant_id:
            raise AuthorizationError("approval request is not available to this tenant")
        updated = replace(request, approved=True)
        self._approvals[request_id] = updated
        return updated

    def _company_for(self, principal: Principal, company_id: str) -> CompanyRecord:
        record = self._companies.get(company_id)
        if record is None or record.tenant_id != principal.tenant_id:
            raise AuthorizationError("company is not available to this tenant")
        return record

    @staticmethod
    def _require(principal: Principal, scope: Scope) -> None:
        if not principal.can(scope):
            raise AuthorizationError(f"required scope: {scope.value}")
