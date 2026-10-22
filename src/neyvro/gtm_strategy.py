"""Knowledge-safe GTM strategy recommendation and disabled backend contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


CONTRACTS = (
    "neyvro_get_customer_context",
    "neyvro_get_gtm_strategy",
    "neyvro_propose_gtm_strategy",
)


@dataclass(frozen=True)
class CustomerContext:
    product: str
    deal_value_usd: float | None = None
    sales_cycle_days: int | None = None
    industries: tuple[str, ...] = ()
    regions: tuple[str, ...] = ()
    buyer_personas: tuple[str, ...] = ()
    self_serve: bool | None = None
    time_to_value_days: int | None = None
    implementation_days: int | None = None
    problem_searchable: bool | None = None
    regulated: bool | None = None
    team_capacity: str | None = None
    evidence: tuple[str, ...] = ()
    research_gaps: tuple[str, ...] = ()


@dataclass(frozen=True)
class StrategyRecommendation:
    recommended_motion: str
    supporting_motion: str | None
    reasons: tuple[str, ...]
    assumptions: tuple[str, ...]
    priority_channels: tuple[str, ...]
    low_priority_channels: tuple[str, ...]
    buyer_personas: tuple[str, ...]
    plan_30_60_90: dict[str, tuple[str, ...]]
    metrics: tuple[str, ...]
    research_gaps: tuple[str, ...]
    connected: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "recommended_motion": self.recommended_motion,
            "supporting_motion": self.supporting_motion,
            "reasons": list(self.reasons),
            "assumptions": list(self.assumptions),
            "priority_channels": list(self.priority_channels),
            "low_priority_channels": list(self.low_priority_channels),
            "buyer_personas": list(self.buyer_personas),
            "plan_30_60_90": {key: list(value) for key, value in self.plan_30_60_90.items()},
            "metrics": list(self.metrics),
            "research_gaps": list(self.research_gaps),
            "connected": self.connected,
        }


def recommend_strategy(context: CustomerContext) -> StrategyRecommendation:
    """Recommend a lead motion from supplied facts without network access."""
    reasons: list[str] = []
    assumptions = list(context.research_gaps)
    gaps = list(context.research_gaps)

    low_value = context.deal_value_usd is not None and context.deal_value_usd < 1_000
    high_value = context.deal_value_usd is not None and context.deal_value_usd >= 25_000
    enterprise_cycle = context.sales_cycle_days is not None and context.sales_cycle_days > 90
    fast_self_serve = context.self_serve is True and (context.time_to_value_days or 999) <= 7
    high_friction = (context.implementation_days or 0) > 30 or context.regulated is True

    if fast_self_serve or low_value:
        lead = "product-led growth"
        support = "inbound/content"
        reasons.append("Self-serve or low deal value makes scalable activation more economical than sustained one-to-one outreach.")
        priority = ["product onboarding", "lifecycle education", "SEO/content"]
        low_priority = ["high-volume cold outbound", "complex partner channel"]
    elif high_value or enterprise_cycle or high_friction:
        lead = "outbound / sales-led"
        support = "partnerships / channel" if context.regulated or high_friction else "inbound/content"
        reasons.append("High value, long cycle, or implementation/compliance friction supports human-led, trust-building sales.")
        priority = ["targeted account research", "evidence-backed outbound", "referrals or expert partners"]
        low_priority = ["broad self-serve PLG", "undifferentiated paid acquisition"]
    elif context.deal_value_usd is not None:
        lead = "outbound / sales-led"
        support = "inbound/content"
        reasons.append("The stated deal value can support focused human selling while content compounds future demand.")
        priority = ["focused outbound", "ICP-led content", "referrals"]
        low_priority = ["running every social channel", "broad untargeted outbound"]
    else:
        lead = "unknown"
        support = None
        reasons.append("Deal value and buying friction are not known well enough to select a motion safely.")
        priority = ["customer interviews", "pricing and sales-cycle discovery"]
        low_priority = ["scaling any paid or outbound channel"]
        gaps.extend(["typical deal value", "sales cycle", "time-to-value", "buyer and buying process"])

    if context.problem_searchable is True:
        if "SEO/content" not in priority and "ICP-led content" not in priority:
            priority.append("SEO/content")
        reasons.append("The problem is reported as searchable, so answer-first content is a viable supporting test.")
    elif context.problem_searchable is None:
        gaps.append("whether target buyers actively search for the problem")

    if not context.industries:
        gaps.append("target industries")
    if not context.regions:
        gaps.append("priority regions")
    if not context.buyer_personas:
        gaps.append("economic buyer and champion")
    if context.deal_value_usd is None:
        gaps.append("typical deal value")
    if context.sales_cycle_days is None:
        gaps.append("sales cycle")
    if context.time_to_value_days is None:
        gaps.append("time-to-value")
    if not context.evidence:
        assumptions.append("Recommendation is based on customer-stated context only; no linked Neyvro evidence was supplied.")

    plan = {
        "days_0_30": (f"Choose one {lead} experiment for one ICP segment.", "Confirm economics, buyer, trigger, and baseline metrics.", "Define stop conditions and evidence required before expansion."),
        "days_31_60": ("Review qualified conversations, activation, conversion, and cycle-time evidence.", "Add at most one supporting channel if the lead experiment has a positive signal.", "Cut channels that add activity without learning or qualified outcomes."),
        "days_61_90": ("Scale only the repeatable motion within team capacity.", "Document the next experiment, owner, budget, and success gate.", "Re-score the motion using observed results and updated research gaps."),
    }
    metrics = (
        "qualified opportunities per target account or activated user",
        "conversion rate with an explicit denominator",
        "sales cycle or time-to-value",
        "cost or capacity per qualified outcome",
        "retention/expansion signal appropriate to the motion",
    )
    return StrategyRecommendation(lead, support, tuple(dict.fromkeys(reasons)), tuple(dict.fromkeys(assumptions)), tuple(priority), tuple(low_priority), context.buyer_personas, plan, metrics, tuple(dict.fromkeys(gaps)))


def safe_contract(name: str, payload: dict[str, Any], transport: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None) -> dict[str, Any]:
    """Call a real adapter only when injected; otherwise fail closed."""
    if name not in CONTRACTS:
        raise ValueError(f"unknown GTM strategy contract: {name}")
    if transport is None:
        return {"status": "disabled", "contract": name, "reason": "Neyvro backend adapter is not configured", "data": None}
    return transport(name, payload)
