from argparse import Namespace
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.run_mcp_real_e2e import EXPECTED_OPERATIONS, run


def test_real_runner_refuses_non_loopback_targets():
    report = run(Namespace(gateway="https://example.invalid", backend="http://127.0.0.1:8001", token_env="NEYVRO_E2E_TOKEN_A", timeout=0.1))
    assert report["status"] == "BLOCKED"
    assert len(report["tool_results"]) == 30
    assert all(item["status"] == "BLOCKED" for item in report["tool_results"])


def test_real_runner_reports_unavailable_local_stack_without_secrets(monkeypatch):
    monkeypatch.delenv("NEYVRO_E2E_TOKEN_A", raising=False)
    report = run(Namespace(gateway="http://127.0.0.1:8000", backend="http://127.0.0.1:8001", token_env="NEYVRO_E2E_TOKEN_A", timeout=0.1))
    assert report["status"] == "BLOCKED"
    assert len(EXPECTED_OPERATIONS) == 14
    assert report["contract"]["expected_tools"] == 30
    assert "Bearer" not in str(report)
