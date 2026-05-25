import pytest

from binance50.backtest.analytics.report_models import BacktestReportPack
from binance50.config.models import AppConfig
from binance50.core.exceptions import BacktestReportingSafetyError, LivePerformanceClaimError
from binance50.safety.backtest_reporting_guard import (
    assert_backtest_reporting_config_safe,
    assert_no_live_performance_claims,
    assert_report_disclaimer_present,
    assert_report_hashes_present,
    build_backtest_reporting_safety_report,
)


def test_assert_backtest_reporting_config_safe():
    config = AppConfig()
    assert_backtest_reporting_config_safe(config)  # default is safe

    # We can't actually change Literal[True] via pydantic easily without error,
    # so just testing the pass case.


def test_assert_no_live_performance_claims():
    assert_no_live_performance_claims("This is a simulation.")

    with pytest.raises(LivePerformanceClaimError):
        assert_no_live_performance_claims("Provides guaranteed profit")


def test_assert_report_disclaimer_present():
    pack = BacktestReportPack(report_id="1", run_id="1", disclaimer="Test")
    assert_report_disclaimer_present(pack)

    pack.disclaimer = ""
    with pytest.raises(BacktestReportingSafetyError):
        assert_report_disclaimer_present(pack)


def test_assert_report_hashes_present():
    pack = BacktestReportPack(
        report_id="1", run_id="1", input_hash="a", config_hash="b", report_hash="c"
    )
    assert_report_hashes_present(pack)

    pack.report_hash = ""
    with pytest.raises(BacktestReportingSafetyError):
        assert_report_hashes_present(pack)


def test_build_backtest_reporting_safety_report():
    config = AppConfig()
    report = build_backtest_reporting_safety_report(config)
    assert report["status"] == "passed"
