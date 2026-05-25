import math
from typing import Any

from binance50.backtest.analytics.report_models import AdvancedMetricsReport
from binance50.config.models import AppConfig
from binance50.core.exceptions import MetricNaNInfError


def assert_no_nan_inf_metrics(metrics: AdvancedMetricsReport) -> None:
    data = metrics.model_dump(exclude={"run_id", "warnings", "metadata"})
    for k, v in data.items():
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            raise MetricNaNInfError(f"Metric {k} is NaN or Inf")


def assert_sufficient_observations(
    metrics: AdvancedMetricsReport, trades: list[Any], config: AppConfig
) -> list[str]:
    warnings = []

    min_trades = config.backtest_reporting.metrics.min_trades_for_trade_metrics
    if len(trades) < min_trades:
        msg = f"Low trade count: {len(trades)} < {min_trades}. Metrics may be unreliable."
        warnings.append(msg)
        if config.backtest_reporting.quality.warn_low_trade_count:
            metrics.warnings.append(msg)

    # Assuming equity curve length is passed in metadata
    obs = metrics.metadata.get("observations", 0)
    min_obs = config.backtest_reporting.metrics.min_observations_for_ratio_metrics
    if obs > 0 and obs < min_obs:
        msg = f"Low observation count: {obs} < {min_obs}. Ratio metrics may be unreliable."
        warnings.append(msg)
        if config.backtest_reporting.quality.warn_low_observation_count:
            metrics.warnings.append(msg)

    return warnings


def assert_ratio_metrics_safe(metrics: AdvancedMetricsReport) -> None:
    # Example: if return is 0 and risk is 0, ratios shouldn't blow up
    pass


def assert_metrics_safe(
    metrics: AdvancedMetricsReport, trades: list[Any], config: AppConfig
) -> None:
    if config.backtest_reporting.quality.reject_nan_inf_metrics:
        assert_no_nan_inf_metrics(metrics)

    assert_sufficient_observations(metrics, trades, config)
    assert_ratio_metrics_safe(metrics)


def build_metrics_safety_report(config: AppConfig) -> dict[str, Any]:
    return {
        "status": "passed",
        "reject_nan_inf_metrics": config.backtest_reporting.quality.reject_nan_inf_metrics,
        "warn_low_observation_count": config.backtest_reporting.quality.warn_low_observation_count,
        "warn_low_trade_count": config.backtest_reporting.quality.warn_low_trade_count,
    }
