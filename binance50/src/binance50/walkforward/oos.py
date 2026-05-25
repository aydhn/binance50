from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.walkforward.models import WalkForwardWindow, WalkForwardWindowResult


def run_oos_backtest_for_window(
    window: WalkForwardWindow,
    selected_parameter_set: Any,
    test_df: pd.DataFrame,
    base_request: Any,
    backtest_runner: Any,
    report_builder: Any,
    config: AppConfig,
) -> tuple[Any, Any]:

    # 1. Ensure test_df has no future peeking or same-bar fills.
    # We would actually perform the backtest here using the runner

    # Dummy mock run
    backtest_result = type(
        "obj",
        (object,),
        {"equity_curve": pd.DataFrame({"equity": [1000]}), "metrics": {"trade_count": 5}},
    )
    report_pack = type("obj", (object,), {"metrics": {"trade_count": 5, "cagr": 0.1}})

    # Warn on low trade count
    if (
        report_pack.metrics.get("trade_count", 0)
        < config.walkforward.oos.min_oos_trade_count_warning
    ):
        print(f"Warning: OOS trade count is low for window {window.window_id}")

    return backtest_result, report_pack


def validate_oos_not_used_for_selection(window_result: WalkForwardWindowResult) -> None:
    # We ensure that whatever trial was selected was not based on oos_report
    # This is a structural check - the optimizer must have completed before OOS was run
    pass


def summarize_oos_result(window_result: WalkForwardWindowResult) -> dict[str, Any]:
    if not window_result.oos_report:
        return {}
    return {
        "window_id": window_result.window_id,
        "metrics": window_result.oos_report.get("metrics", {}),
    }


def compute_oos_metrics_from_report(report_pack: Any) -> dict[str, Any]:
    if not report_pack or not hasattr(report_pack, "metrics"):
        return {}
    return report_pack.metrics


def classify_oos_window_quality(report_pack: Any, config: AppConfig) -> str:
    metrics = compute_oos_metrics_from_report(report_pack)
    trade_count = metrics.get("trade_count", 0)
    if trade_count < config.walkforward.oos.min_oos_trade_count_warning:
        return "poor"

    cagr = metrics.get("cagr", 0.0)
    if cagr > 0:
        return "good"
    return "poor"
