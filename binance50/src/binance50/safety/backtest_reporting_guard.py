from typing import Any

from binance50.backtest.analytics.report_models import BacktestReportPack
from binance50.config.models import AppConfig
from binance50.core.exceptions import BacktestReportingSafetyError, LivePerformanceClaimError


def assert_backtest_reporting_config_safe(config: AppConfig) -> None:
    if not config.backtest_reporting.no_live_claims:
        raise BacktestReportingSafetyError("no_live_claims must be True")
    if not config.backtest_reporting.require_disclaimer:
        raise BacktestReportingSafetyError("require_disclaimer must be True")
    if not config.backtest_reporting.require_report_hash:
        raise BacktestReportingSafetyError("require_report_hash must be True")


def assert_no_live_performance_claims(text_or_payload: Any) -> None:
    text = str(text_or_payload).lower()
    forbidden_phrases = ["guaranteed profit", "kesin kazanç", "live proven"]
    for phrase in forbidden_phrases:
        if phrase in text:
            raise LivePerformanceClaimError(f"Forbidden phrase detected: {phrase}")


def assert_report_disclaimer_present(pack: BacktestReportPack) -> None:
    if not pack.disclaimer:
        raise BacktestReportingSafetyError("Missing disclaimer in report pack")


def assert_report_hashes_present(pack: BacktestReportPack) -> None:
    if not pack.input_hash or not pack.config_hash or not pack.report_hash:
        raise BacktestReportingSafetyError("Missing required hashes in report pack")


def assert_report_pack_safe(pack: BacktestReportPack, config: AppConfig) -> None:
    assert_backtest_reporting_config_safe(config)
    assert_report_disclaimer_present(pack)
    assert_report_hashes_present(pack)
    assert_no_live_performance_claims(pack.disclaimer)


def build_backtest_reporting_safety_report(config: AppConfig) -> dict[str, Any]:
    try:
        assert_backtest_reporting_config_safe(config)
        return {"status": "passed", "issues": []}
    except Exception as e:
        return {"status": "failed", "issues": [str(e)]}
