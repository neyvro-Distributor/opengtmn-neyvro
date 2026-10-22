import pytest

from neyvro.models import Evidence, Principal, Scope
from neyvro.service import AuthorizationError, TenantStore
from neyvro.skills import SKILLS, validate_catalog


def principal(tenant_id: str, *scopes: Scope) -> Principal:
    return Principal(f"user-{tenant_id}", tenant_id, frozenset(scopes))


def test_skill_catalog_has_all_contracts() -> None:
    validate_catalog()
    assert len(SKILLS) == 27


def test_tenant_isolation_and_scope_enforcement() -> None:
    store = TenantStore()
    owner = principal("tenant-a", Scope.WRITE_PROPOSALS, Scope.READ_INTELLIGENCE)
    other = principal("tenant-b", Scope.READ_INTELLIGENCE)
    store.add_company(owner, "acme", "Acme")

    with pytest.raises(AuthorizationError):
        store.get_company(other, "acme")

    with pytest.raises(AuthorizationError):
        store.add_company(other, "other", "Other")


def test_evidence_and_approval_flow_requires_send_scope() -> None:
    store = TenantStore()
    writer = principal("tenant-a", Scope.WRITE_PROPOSALS, Scope.READ_INTELLIGENCE)
    sender = principal("tenant-a", Scope.SEND_MESSAGES)
    store.add_company(writer, "acme", "Acme")
    store.add_evidence(writer, "acme", Evidence("crm", "Acme opened a new office"))
    request = store.propose_action(writer, "send_email", {"company_id": "acme"})

    with pytest.raises(AuthorizationError):
        store.approve_action(writer, request.request_id)

    approved = store.approve_action(sender, request.request_id)
    assert approved.approved is True
