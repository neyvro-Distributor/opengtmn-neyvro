from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4


class Scope(StrEnum):
    READ_INTELLIGENCE = "intelligence:read"
    WRITE_PROPOSALS = "proposals:write"
    SEND_MESSAGES = "messages:send"


@dataclass(frozen=True)
class Principal:
    subject: str
    tenant_id: str
    scopes: frozenset[Scope]

    def can(self, scope: Scope) -> bool:
        return scope in self.scopes


@dataclass(frozen=True)
class Evidence:
    source: str
    statement: str
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CompanyRecord:
    company_id: str
    tenant_id: str
    name: str
    evidence: list[Evidence] = field(default_factory=list)


@dataclass(frozen=True)
class ApprovalRequest:
    request_id: str
    tenant_id: str
    action: str
    payload: dict[str, str]
    approved: bool = False

    @classmethod
    def create(cls, tenant_id: str, action: str, payload: dict[str, str]) -> "ApprovalRequest":
        return cls(str(uuid4()), tenant_id, action, payload)
