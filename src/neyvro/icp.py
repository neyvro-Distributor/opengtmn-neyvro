"""Evidence-backed ICP modeling and safe, adapter-only integration contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


CONTRACTS = (
    "neyvro_get_icp",
    "neyvro_evaluate_icp_fit",
    "neyvro_propose_icp_changes",
)

DEFAULT_WEIGHTS = {
    "industry": 20,
    "size": 15,
    "geography": 10,
    "technology": 15,
    "buyer": 15,
    "problem": 15,
    "trigger": 10,
}


@dataclass(frozen=True)
class Evidence:
    source: str
    statement: str
    dimension: str
    confidence: float = 1.0


@dataclass(frozen=True)
class ICPProfile:
    name: str
    industries: tuple[str, ...] = ()
    excluded_industries: tuple[str, ...] = ()
    geographies: tuple[str, ...] = ()
    excluded_geographies: tuple[str, ...] = ()
    min_employees: int | None = None
    max_employees: int | None = None
    min_revenue_usd: float | None = None
    max_revenue_usd: float | None = None
    technologies: tuple[str, ...] = ()
    excluded_technologies: tuple[str, ...] = ()
    buyer_personas: tuple[str, ...] = ()
    problems: tuple[str, ...] = ()
    triggers: tuple[str, ...] = ()
    excluded_company_types: tuple[str, ...] = ()
    weights: tuple[tuple[str, int], ...] = tuple(DEFAULT_WEIGHTS.items())
    version: str = "1.0"

    def weight_map(self) -> dict[str, int]:
        result = dict(DEFAULT_WEIGHTS)
        result.update(dict(self.weights))
        return result


@dataclass(frozen=True)
class CompanySignals:
    company_id: str
    name: str
    industry: str | None = None
    company_type: str | None = None
    employees: int | None = None
    revenue_usd: float | None = None
    geography: str | None = None
    technologies: tuple[str, ...] = ()
    buyer_roles: tuple[str, ...] = ()
    problems: tuple[str, ...] = ()
    triggers: tuple[str, ...] = ()
    evidence: tuple[Evidence, ...] = ()


@dataclass(frozen=True)
class ICPFit:
    company_id: str
    company_name: str
    status: str
    score: int
    tier: str
    matched_dimensions: tuple[str, ...]
    missing_dimensions: tuple[str, ...]
    disqualifiers: tuple[str, ...]
    reasons: tuple[str, ...]
    evidence: tuple[Evidence, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "company_id": self.company_id,
            "company_name": self.company_name,
            "status": self.status,
            "score": self.score,
            "tier": self.tier,
            "matched_dimensions": list(self.matched_dimensions),
            "missing_dimensions": list(self.missing_dimensions),
            "disqualifiers": list(self.disqualifiers),
            "reasons": list(self.reasons),
            "evidence": [e.__dict__ for e in self.evidence],
        }


def _norm(values: tuple[str, ...] | list[str]) -> set[str]:
    return {value.strip().casefold() for value in values if value.strip()}


def _has_evidence(company: CompanySignals, dimension: str) -> bool:
    return any(item.dimension == dimension and item.confidence > 0 for item in company.evidence)


def evaluate_icp_fit(profile: ICPProfile, company: CompanySignals) -> ICPFit:
    """Evaluate one company without network access or persistence."""
    weights = profile.weight_map()
    matched: list[str] = []
    mismatched: list[str] = []
    missing: list[str] = []
    reasons: list[str] = []
    disqualifiers: list[str] = []
    points = 0
    company_industry = (company.industry or "").casefold()
    company_geo = (company.geography or "").casefold()
    company_type = (company.company_type or "").casefold()
    technologies = _norm(company.technologies)

    if company_industry in _norm(profile.excluded_industries):
        disqualifiers.append(f"excluded industry: {company.industry}")
    if company_geo in _norm(profile.excluded_geographies):
        disqualifiers.append(f"excluded geography: {company.geography}")
    if company_type in _norm(profile.excluded_company_types):
        disqualifiers.append(f"excluded company type: {company.company_type}")
    excluded_tech = technologies & _norm(profile.excluded_technologies)
    if excluded_tech:
        disqualifiers.append(f"excluded technology: {', '.join(sorted(excluded_tech))}")

    def mark(dimension: str, condition: bool, unknown: bool, reason: str) -> None:
        nonlocal points
        if condition and _has_evidence(company, dimension):
            matched.append(dimension)
            points += weights.get(dimension, 0)
            reasons.append(reason)
        elif unknown:
            missing.append(dimension)
        else:
            mismatched.append(dimension)
            reasons.append(f"does not match {dimension}: {reason}")

    mark("industry", bool(company_industry and company_industry in _norm(profile.industries)), not company_industry, f"industry {company.industry or 'unknown'}")
    size_ok = company.employees is not None and (profile.min_employees is None or company.employees >= profile.min_employees) and (profile.max_employees is None or company.employees <= profile.max_employees) and (profile.min_revenue_usd is None or (company.revenue_usd is not None and company.revenue_usd >= profile.min_revenue_usd)) and (profile.max_revenue_usd is None or (company.revenue_usd is not None and company.revenue_usd <= profile.max_revenue_usd))
    mark("size", size_ok, company.employees is None or (company.revenue_usd is None and (profile.min_revenue_usd is not None or profile.max_revenue_usd is not None)), f"employees {company.employees if company.employees is not None else 'unknown'}")
    mark("geography", bool(company_geo and company_geo in _norm(profile.geographies)), not company_geo, f"geography {company.geography or 'unknown'}")
    required_tech = _norm(profile.technologies)
    tech_ok = not required_tech or required_tech.issubset(technologies)
    mark("technology", tech_ok, not technologies, f"technology evidence {sorted(technologies) or 'unknown'}")
    buyer_ok = bool(_norm(company.buyer_roles) & _norm(profile.buyer_personas))
    mark("buyer", buyer_ok, not company.buyer_roles, f"buyer roles {company.buyer_roles or ('unknown',)}")
    problem_ok = bool(_norm(company.problems) & _norm(profile.problems))
    mark("problem", problem_ok, not company.problems, f"problems {company.problems or ('unknown',)}")
    trigger_ok = bool(_norm(company.triggers) & _norm(profile.triggers))
    mark("trigger", trigger_ok, not company.triggers, f"triggers {company.triggers or ('unknown',)}")

    evidence_dimensions = {item.dimension for item in company.evidence if item.confidence > 0}
    missing.extend(sorted({dimension for dimension in ("industry", "size", "geography", "technology", "buyer", "problem", "trigger") if dimension not in evidence_dimensions and dimension not in missing and dimension not in matched}))
    score = min(100, max(0, points))
    tier = "A" if score >= 80 else "B" if score >= 60 else "C"
    if disqualifiers:
        status = "disqualified"
        tier = "C"
    elif score < 60 and len(mismatched) >= 2:
        status = "nonmatching"
    elif len(matched) < 2 or len(evidence_dimensions) < 2 or len(missing) >= 3:
        status = "incomplete"
        reasons.append("At least two corroborating dimensions and evidence records are required; one signal cannot qualify a company.")
    elif score >= 60:
        status = "qualified"
    else:
        status = "nonmatching"
    return ICPFit(company.company_id, company.name, status, score, tier, tuple(dict.fromkeys(matched)), tuple(dict.fromkeys(missing)), tuple(disqualifiers), tuple(dict.fromkeys(reasons)), company.evidence)


def safe_contract(name: str, payload: dict[str, Any], transport: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None) -> dict[str, Any]:
    """Use an injected Neyvro adapter only; otherwise return a disabled result."""
    if name not in CONTRACTS:
        raise ValueError(f"unknown ICP contract: {name}")
    if transport is None:
        return {"status": "disabled", "contract": name, "reason": "Neyvro ICP backend adapter is not configured", "data": None}
    return transport(name, payload)
