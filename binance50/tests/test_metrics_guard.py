import math

import pytest

from binance50.backtest.analytics.report_models import AdvancedMetricsReport
from binance50.config.models import AppConfig
from binance50.core.exceptions import MetricNaNInfError
from binance50.safety.metrics_guard import (
    assert_no_nan_inf_metrics,
    assert_sufficient_observations,
    build_metrics_safety_report,
)


def test_assert_no_nan_inf_metrics():
    metrics = AdvancedMetricsReport(run_id="1", cagr_pct=10.0)
    assert_no_nan_inf_metrics(metrics)

    metrics.sharpe_ratio = math.nan
    with pytest.raises(MetricNaNInfError):
        assert_no_nan_inf_metrics(metrics)


def test_assert_sufficient_observations():
    config = AppConfig()
    config.backtest_reporting.metrics.min_trades_for_trade_metrics = 5

    metrics = AdvancedMetricsReport(run_id="1")
    trades = [1, 2]  # length 2 < 5

    warnings = assert_sufficient_observations(metrics, trades, config)
    assert len(warnings) == 1
    assert "Low trade count" in warnings[0]
    assert len(metrics.warnings) == 1


def test_build_metrics_safety_report():
    config = AppConfig()
    report = build_metrics_safety_report(config)
    assert report["status"] == "passed"
    assert report["reject_nan_inf_metrics"] is True
