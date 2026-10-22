from neyvro.positioning import ProductContext, ProofPoint, generate_positioning, safe_contract


def test_security_persona_gets_evidence_safe_positioning() -> None:
    result = generate_positioning(ProductContext(
        product_name="Neyvro Shield",
        category="cloud security platform",
        capabilities=("continuous evidence monitoring", "automated compliance reporting"),
        alternatives=("spreadsheets", "manual audits"),
        customer_problems=("security teams cannot keep evidence current",),
        personas=("CISO", "security engineering leader"),
        approved_claims=("continuous evidence monitoring",),
        proof_points=(ProofPoint("continuous evidence monitoring", "approved-case-1", True), ProofPoint("automated compliance reporting", "draft-claim", False)),
        approved_positioning="Approved security positioning v1",
        version="1.2.0",
        evidence=("onboarding:product", "customer-interview:42"),
    ), persona="CISO")
    assert result.target_persona["name"] == "CISO"
    assert result.version == "1.2.0"
    assert result.approval_status == "needs_approval"
    assert len(result.proof_points) == 1
    assert "automated compliance reporting" in result.unsupported_claims


def test_developer_persona_has_buyer_specific_angle() -> None:
    result = generate_positioning(ProductContext(
        product_name="TraceKit",
        category="developer observability",
        capabilities=("fast local setup",),
        alternatives=("homegrown dashboards",),
        customer_problems=("developers lose time debugging distributed failures",),
        personas=("staff engineer", "platform lead"),
        approved_claims=("fast local setup",),
    ), persona="staff engineer")
    assert result.target_persona["name"] == "staff engineer"
    assert result.positioning_summary["before_after_bridge"]["before"]
    assert result.message_angles[0]["persona"] == "staff engineer"


def test_incomplete_product_information_is_explicit() -> None:
    result = generate_positioning(ProductContext(product_name="New Product"))
    assert result.approval_status == "needs_approval"
    assert "product category is not confirmed" in result.unsupported_claims
    assert "customer problem is not confirmed" in result.unsupported_claims
    assert result.target_persona["status"] == "unknown"


def test_positioning_backend_is_disabled_without_adapter() -> None:
    result = safe_contract("neyvro_get_approved_claims", {"workspace_id": "w1"})
    assert result["status"] == "disabled"
    assert result["data"] is None
