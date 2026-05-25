from typing import Any

from binance50.backtest.analytics.report_models import BacktestReportPack
from binance50.backtest.analytics.report_pack import BacktestReportPackBuilder
from binance50.config.models import AppConfig


def build_backtest_report_pack(result: Any, config: AppConfig) -> BacktestReportPack:
    builder = BacktestReportPackBuilder(config)
    return builder.build(result)


def build_backtest_report_summary(pack: BacktestReportPack) -> dict[str, Any]:
    return pack.summary


def build_metrics_table(pack: BacktestReportPack) -> list[dict[str, Any]]:
    if not pack.advanced_metrics:
        return []

    metrics_dict = pack.advanced_metrics.model_dump(exclude={"run_id", "warnings", "metadata"})
    table = []
    for k, v in metrics_dict.items():
        table.append({"metric": k, "value": v})
    return table


def build_periodic_returns_table(pack: BacktestReportPack) -> list[dict[str, Any]]:
    table = []
    for pr in pack.periodic_returns:
        # Just grab the summary for the CLI
        table.append(
            {
                "frequency": pr.frequency,
                "best_period": pr.best_period,
                "worst_period": pr.worst_period,
                "positive_ratio": pr.positive_period_ratio,
            }
        )
    return table


def build_drawdown_table(pack: BacktestReportPack) -> list[dict[str, Any]]:
    if not pack.drawdowns:
        return []
    # Assume it returns the list of top drawdowns directly or in a key
    return pack.drawdowns


def build_trade_distribution_table(pack: BacktestReportPack) -> list[dict[str, Any]]:
    # Represent distribution as key/value
    dist = pack.trade_distribution
    if not dist:
        return []

    table = []
    for k, v in dist.items():
        if isinstance(v, (int, float, str, bool)):
            table.append({"metric": k, "value": v})
    return table


def build_breakdown_tables(pack: BacktestReportPack) -> dict[str, list[dict[str, Any]]]:
    tables = {}
    for k, v in pack.breakdowns.items():
        if isinstance(v, dict) and "table" in v:
            tables[k] = v["table"]
    return tables


def build_report_health(config: AppConfig) -> dict[str, Any]:
    return {
        "status": "healthy",
        "real_exchange_forbidden": config.backtest_reporting.real_exchange_forbidden,
        "no_live_claims": config.backtest_reporting.no_live_claims,
        "require_disclaimer": config.backtest_reporting.require_disclaimer,
    }
