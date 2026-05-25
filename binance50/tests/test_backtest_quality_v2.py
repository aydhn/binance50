import math

import pytest

from binance50.backtest.analytics.report_models import AdvancedMetricsReport, BacktestReportPack
from binance50.backtest.quality_v2 import (
    assert_backtest_report_quality_passed,
    build_backtest_report_quality,
    detect_live_performance_claims,
    detect_missing_disclaimer,
    detect_missing_hashes,
    detect_missing_sections,
    detect_nan_inf_metrics,
)
from binance50.config.models import AppConfig
from binance50.core.exceptions import BacktestReportQualityError


@pytest.fixture
def base_pack():
    return BacktestReportPack(report_id="1", run_id="1")


def test_detect_nan_inf_metrics(base_pack):
    metrics = AdvancedMetricsReport(run_id="1", cagr_pct=math.nan)
    base_pack.advanced_metrics = metrics
    issues = detect_nan_inf_metrics(base_pack)
    assert len(issues) == 1
    assert issues[0].issue_type == "nan_inf_metric"


def test_detect_missing_sections(base_pack):
    issues = detect_missing_sections(base_pack)
    assert len(issues) == 1
    assert issues[0].issue_type == "missing_section"


def test_detect_missing_disclaimer(base_pack):
    issues = detect_missing_disclaimer(base_pack)
    assert len(issues) == 1
    assert issues[0].issue_type == "missing_disclaimer"


def test_detect_missing_hashes(base_pack):
    issues = detect_missing_hashes(base_pack)
    assert len(issues) == 1
    assert issues[0].issue_type == "missing_hash"


def test_detect_live_performance_claims(base_pack):
    base_pack.disclaimer = "This is a guaranteed profit system"
    issues = detect_live_performance_claims(base_pack)
    assert len(issues) == 1
    assert issues[0].issue_type == "live_performance_claim"


def test_assert_backtest_report_quality_passed():
    config = AppConfig()
    pack = BacktestReportPack(report_id="1", run_id="1")
    report = build_backtest_report_quality(pack, config)

    with pytest.raises(BacktestReportQualityError):
        assert_backtest_report_quality_passed(report, config)
