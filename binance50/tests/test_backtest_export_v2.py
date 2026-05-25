import json

import pytest

from binance50.backtest.analytics.report_models import AdvancedMetricsReport, BacktestReportPack
from binance50.backtest.export_v2 import (
    export_metrics_to_csv,
    export_report_pack_to_json,
    export_report_pack_to_markdown,
    export_static_html_skeleton,
)


@pytest.fixture
def sample_pack():
    metrics = AdvancedMetricsReport(run_id="1", cagr_pct=10.0, sharpe_ratio=1.5)
    return BacktestReportPack(
        report_id="123",
        run_id="1",
        summary={"strategy": "test_strat"},
        disclaimer="Test Disclaimer",
        report_hash="abc",
        advanced_metrics=metrics,
        trade_distribution={"wins": 5, "losses": 2},
    )


def test_export_json(tmp_path, sample_pack):
    out = tmp_path / "report.json"
    export_report_pack_to_json(sample_pack, out)
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["report_id"] == "123"


def test_export_markdown(tmp_path, sample_pack):
    out = tmp_path / "report.md"
    export_report_pack_to_markdown(sample_pack, out)
    assert out.exists()
    content = out.read_text()
    assert "# Backtest Report: 123" in content
    assert "Test Disclaimer" in content
    assert "`abc`" in content


def test_export_metrics_csv(tmp_path, sample_pack):
    out = tmp_path / "metrics.csv"
    export_metrics_to_csv(sample_pack, out)
    assert out.exists()
    content = out.read_text()
    assert "metric,value" in content
    assert "cagr_pct,10.0" in content


def test_export_html_skeleton(tmp_path, sample_pack):
    out = tmp_path / "report.html"
    export_static_html_skeleton(sample_pack, out)
    assert out.exists()
    content = out.read_text()
    assert "<html>" in content
    assert "Test Disclaimer" in content
