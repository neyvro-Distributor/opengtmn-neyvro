import json
from pathlib import Path

from neyvro.gtm_strategy import CustomerContext, recommend_strategy, safe_contract


def test_smb_saas_prefers_plg_and_inbound() -> None:
    result = recommend_strategy(CustomerContext(
        product="self-serve scheduling SaaS",
        deal_value_usd=600,
        sales_cycle_days=7,
        self_serve=True,
        time_to_value_days=1,
        industries=("professional services",),
        regions=("US",),
        buyer_personas=("operations manager",),
        problem_searchable=True,
    ))
    assert result.recommended_motion == "product-led growth"
    assert result.supporting_motion == "inbound/content"
    assert "product onboarding" in result.priority_channels
    assert result.connected is False


def test_enterprise_security_prefers_sales_led_and_partners() -> None:
    result = recommend_strategy(CustomerContext(
        product="enterprise security platform",
        deal_value_usd=120_000,
        sales_cycle_days=180,
        implementation_days=90,
        regulated=True,
        industries=("financial services",),
        regions=("North America", "EU"),
        buyer_personas=("CISO", "security engineering leader"),
        evidence=("customer interview:e1",),
    ))
    assert result.recommended_motion == "outbound / sales-led"
    assert result.supporting_motion == "partnerships / channel"
    assert "broad self-serve PLG" in result.low_priority_channels


def test_developer_tool_with_unknown_economics_stays_transparent() -> None:
    result = recommend_strategy(CustomerContext(
        product="developer observability tool",
        self_serve=True,
        time_to_value_days=3,
        problem_searchable=True,
        buyer_personas=("staff engineer",),
    ))
    assert result.recommended_motion == "product-led growth"
    assert "typical deal value" in result.research_gaps
    assert result.research_gaps


def test_missing_context_does_not_fabricate_a_motion() -> None:
    result = recommend_strategy(CustomerContext(product="new developer tool"))
    assert result.recommended_motion == "unknown"
    assert "sales cycle" in result.research_gaps
    assert result.assumptions


def test_backend_contracts_are_disabled_without_adapter() -> None:
    result = safe_contract("neyvro_get_customer_context", {"workspace_id": "w1"})
    assert result["status"] == "disabled"
    assert result["data"] is None


def test_gtm_contract_manifest_matches_skill() -> None:
    manifest = json.loads(Path("skills/gtm-strategy/integration.json").read_text())
    assert manifest["skill"] == "gtm-strategy"
    assert manifest["connected_by_default"] is False
    assert {item["name"] for item in manifest["contracts"]} == {
        "neyvro_get_customer_context",
        "neyvro_get_gtm_strategy",
        "neyvro_propose_gtm_strategy",
    }


def test_injected_transport_is_the_only_connected_path() -> None:
    result = safe_contract("neyvro_get_gtm_strategy", {"workspace_id": "w1"}, lambda name, payload: {"status": "available", "name": name, "payload": payload})
    assert result["status"] == "available"
