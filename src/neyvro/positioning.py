"""Evidence-safe product positioning and message-strategy workflows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


CONTRACTS = (
    "neyvro_get_product_context",
    "neyvro_get_positioning",
    "neyvro_propose_positioning",
    "neyvro_get_approved_claims",
)


@dataclass(frozen=True)
class ProofPoint:
    claim: str
    source: str
    approved: bool = False


@dataclass(frozen=True)
class ProductContext:
    product_name: str
    category: str | None = None
    capabilities: tuple[str, ...] = ()
    alternatives: tuple[str, ...] = ()
    customer_problems: tuple[str, ...] = ()
    personas: tuple[str, ...] = ()
    approved_claims: tuple[str, ...] = ()
    proof_points: tuple[ProofPoint, ...] = ()
    brand_voice: str | None = None
    approved_positioning: str | None = None
    version: str = "0.1.0"
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class PositioningDraft:
    version: str
    positioning_summary: dict[str, Any]
    target_persona: dict[str, Any]
    problem_statement: dict[str, Any]
    differentiation: dict[str, Any]
    proof_points: tuple[dict[str, Any], ...]
    message_angles: tuple[dict[str, Any], ...]
    unsupported_claims: tuple[str, ...]
    approval_status: str
    connected: bool = False

    def as_dict(self) -> dict[str, Any]:
        result = self.__dict__.copy()
        result["proof_points"] = list(self.proof_points)
        result["message_angles"] = list(self.message_angles)
        result["unsupported_claims"] = list(self.unsupported_claims)
        return result


def generate_positioning(context: ProductContext, persona: str | None = None) -> PositioningDraft:
    """Create a reviewable positioning draft from supplied facts only."""
    chosen_persona = persona or (context.personas[0] if context.personas else "unknown buyer")
    approved = {claim.casefold() for claim in context.approved_claims}
    proof = tuple(point for point in context.proof_points if point.approved and point.claim.casefold() in approved)
    unsupported = [capability for capability in context.capabilities if capability.casefold() not in approved]
    if not context.category:
        unsupported.append("product category is not confirmed")
    if not context.alternatives:
        unsupported.append("real competitor alternatives are not confirmed")
    if not context.customer_problems:
        unsupported.append("customer problem is not confirmed")
    if not context.personas:
        unsupported.append("target persona is not confirmed")

    problem = context.customer_problems[0] if context.customer_problems else "the customer's confirmed problem is unknown"
    category = context.category or "an unconfirmed category"
    bridge = context.product_name if context.capabilities else "the product's confirmed capabilities"
    before_after = {
        "before": problem,
        "after": "a better outcome for the selected buyer, to be confirmed with customer evidence",
        "bridge": bridge,
    }
    differentiators = [capability for capability in context.capabilities if capability.casefold() in approved]
    if not differentiators:
        differentiators = ["No differentiated capability is approved yet."]
    angles = (
        {"persona": chosen_persona, "angle": f"Help {chosen_persona} move from {problem} to a measurable improved state.", "evidence_required": True},
        {"persona": chosen_persona, "angle": f"Position {context.product_name} as a {category} option against the confirmed alternative.", "evidence_required": True},
    )
    status = "approved" if context.approved_positioning and not unsupported else "needs_approval"
    return PositioningDraft(
        version=context.version,
        positioning_summary={"category": category, "one_liner": f"{context.product_name} helps {chosen_persona} address {problem}.", "before_after_bridge": before_after},
        target_persona={"name": chosen_persona, "evidence": list(context.evidence), "status": "confirmed" if context.personas else "unknown"},
        problem_statement={"problem": problem, "customer_language_required": True, "evidence": list(context.evidence)},
        differentiation={"capabilities": differentiators, "alternatives": list(context.alternatives), "honest_tradeoffs_required": True},
        proof_points=tuple({"claim": point.claim, "source": point.source, "approved": point.approved} for point in proof),
        message_angles=angles,
        unsupported_claims=tuple(dict.fromkeys(unsupported)),
        approval_status=status,
    )


def safe_contract(name: str, payload: dict[str, Any], transport: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None) -> dict[str, Any]:
    """Use a real Neyvro adapter only when injected; otherwise fail closed."""
    if name not in CONTRACTS:
        raise ValueError(f"unknown positioning contract: {name}")
    if transport is None:
        return {"status": "disabled", "contract": name, "reason": "Neyvro positioning backend adapter is not configured", "data": None}
    return transport(name, payload)
