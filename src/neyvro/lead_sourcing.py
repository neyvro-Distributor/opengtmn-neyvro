"""Buyer discovery and contact enrichment with fail-closed list hygiene."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Iterable

CONTRACTS = ("neyvro_search_buyers", "neyvro_get_opportunity_buyers", "neyvro_enrich_contact", "neyvro_get_contact_verification")
VERIFICATION_STATES = {"verified", "unverified", "catch_all", "invalid", "stale", "opted_out", "wrong_company"}
BUYER_CATEGORIES = {"economic_buyer", "champion", "user", "technical_evaluator", "approver", "blocker", "unknown"}


@dataclass(frozen=True)
class AccountCandidate:
    company_id: str
    company: str
    domain: str
    icp_status: str = "qualified"
    existing_customer: bool = False
    open_opportunity: bool = False
    suppressed: bool = False
    disqualifiers: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProviderContact:
    name: str
    company: str
    company_id: str
    current_role: str
    source_provider: str
    source_record_id: str
    email: str | None = None
    email_provenance: str = "unknown"
    verification_status: str = "unverified"
    last_verified_at: datetime | None = None
    opportunity_ids: tuple[str, ...] = ()
    permitted_use: bool = False
    permitted_use_basis: str | None = None
    person_id: str | None = None
    buyer_category: str = "unknown"
    cost_units: int = 0


@dataclass(frozen=True)
class EnrichmentPolicy:
    entitled: bool = False
    usage_budget: int = 0
    used_units: int = 0
    freshness_days: int = 30
    suppressed_emails: frozenset[str] = frozenset()
    suppressed_person_ids: frozenset[str] = frozenset()
    existing_customer_ids: frozenset[str] = frozenset()


@dataclass(frozen=True)
class ProviderResult:
    provider: str
    contacts: tuple[ProviderContact, ...] = ()
    error: str | None = None
    rate_limit_remaining: int | None = None
    paid: bool = False


@dataclass(frozen=True)
class SourcingResult:
    accounts_considered: tuple[str, ...]
    accounts_excluded: tuple[dict[str, str], ...]
    contacts: tuple[dict[str, Any], ...]
    duplicates_removed: tuple[str, ...]
    suppressed_contacts: tuple[str, ...]
    provider_events: tuple[dict[str, Any], ...]
    usage: dict[str, Any]
    research_gaps: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        result = self.__dict__.copy()
        for field in ("accounts_considered", "accounts_excluded", "contacts", "duplicates_removed", "suppressed_contacts", "provider_events", "research_gaps"):
            result[field] = list(result[field])
        return result


def _norm(value: str | None) -> str:
    return " ".join((value or "").casefold().split())


def _email(value: str | None) -> str:
    return (value or "").strip().casefold()


def _fresh(contact: ProviderContact, now: datetime, days: int) -> bool:
    return bool(contact.last_verified_at and contact.last_verified_at >= now - timedelta(days=days))


def _eligible_status(contact: ProviderContact, now: datetime, policy: EnrichmentPolicy) -> str:
    status = contact.verification_status if contact.verification_status in VERIFICATION_STATES else "unverified"
    if status == "verified" and not _fresh(contact, now, policy.freshness_days):
        status = "stale"
    if contact.email_provenance == "pattern_guess" and status == "verified":
        status = "unverified"
    return status


def _contact_dict(contact: ProviderContact, status: str) -> dict[str, Any]:
    return {
        "name": contact.name, "company": contact.company, "current_role": contact.current_role,
        "buyer_category": contact.buyer_category if contact.buyer_category in BUYER_CATEGORIES else "unknown",
        "source": {"provider": contact.source_provider, "record_id": contact.source_record_id},
        "verification_status": status,
        "last_verified_at": contact.last_verified_at.isoformat() if contact.last_verified_at else None,
        "opportunity_ids": list(contact.opportunity_ids),
        "contact_details": {"email": contact.email, "email_provenance": contact.email_provenance, "permitted_use": contact.permitted_use, "permitted_use_basis": contact.permitted_use_basis},
    }


def source_and_enrich(accounts: Iterable[AccountCandidate], provider_results: Iterable[ProviderResult], policy: EnrichmentPolicy = EnrichmentPolicy(), now: datetime | None = None) -> SourcingResult:
    """Apply ICP, suppression, deduplication, waterfall, freshness, and budget rules."""
    now = now or datetime.now(timezone.utc)
    considered: list[str] = []
    excluded: list[dict[str, str]] = []
    eligible: dict[str, AccountCandidate] = {}
    for account in accounts:
        reason = None
        if account.company_id in policy.existing_customer_ids or account.existing_customer:
            reason = "existing_customer"
        elif account.open_opportunity:
            reason = "open_opportunity"
        elif account.suppressed:
            reason = "suppressed_account"
        elif account.disqualifiers:
            reason = "disqualified"
        elif account.icp_status != "qualified":
            reason = f"icp_{account.icp_status}"
        if reason:
            excluded.append({"company_id": account.company_id, "reason": reason})
        else:
            considered.append(account.company_id)
            eligible[account.company_id] = account

    contacts: list[dict[str, Any]] = []
    duplicates: list[str] = []
    suppressed: list[str] = []
    events: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    paid_calls = 0
    used_units = policy.used_units
    gaps: list[str] = []
    for result in provider_results:
        if result.paid and not policy.entitled:
            events.append({"provider": result.provider, "status": "disabled", "reason": "customer enrichment entitlement is absent"})
            gaps.append(f"paid provider {result.provider} requires customer entitlement")
            continue
        if result.paid and used_units >= policy.usage_budget:
            events.append({"provider": result.provider, "status": "blocked", "reason": "usage budget exhausted"})
            gaps.append(f"provider {result.provider} usage budget exhausted")
            continue
        if result.error:
            events.append({"provider": result.provider, "status": "failed", "reason": result.error, "rate_limit_remaining": result.rate_limit_remaining})
            gaps.append(f"provider {result.provider} failed")
            continue
        if result.paid:
            paid_calls += 1
        for contact in result.contacts:
            if contact.company_id not in eligible:
                events.append({"provider": result.provider, "status": "excluded", "record_id": contact.source_record_id, "reason": "wrong_company_or_account_not_eligible"})
                continue
            status = _eligible_status(contact, now, policy)
            norm_email = _email(contact.email)
            key = f"email:{norm_email}" if norm_email else f"person:{_norm(contact.name)}|company:{contact.company_id}|role:{_norm(contact.current_role)}"
            if contact.person_id and contact.person_id in policy.suppressed_person_ids or norm_email and norm_email in policy.suppressed_emails or status == "opted_out":
                suppressed.append(contact.source_record_id)
                continue
            if contact.email_provenance == "pattern_guess" and status == "verified":
                status = "unverified"
            if key in seen_keys:
                duplicates.append(contact.source_record_id)
                continue
            seen_keys.add(key)
            contacts.append(_contact_dict(contact, status))
            used_units += contact.cost_units
    if not contacts:
        gaps.append("no contact passed identity, company-match, verification, and suppression checks")
    return SourcingResult(tuple(considered), tuple(excluded), tuple(contacts), tuple(duplicates), tuple(suppressed), tuple(events), {"entitled": policy.entitled, "budget_units": policy.usage_budget, "used_units": used_units, "paid_calls": paid_calls}, tuple(dict.fromkeys(gaps)))


def safe_contract(name: str, payload: dict[str, Any], transport: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None) -> dict[str, Any]:
    """Call an injected provider/backend adapter, otherwise remain disabled."""
    if name not in CONTRACTS:
        raise ValueError(f"unknown lead-sourcing contract: {name}")
    if transport is None:
        return {"status": "disabled", "contract": name, "reason": "Neyvro buyer/contact provider adapter is not configured", "data": None}
    return transport(name, payload)
