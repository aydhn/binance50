from binance50.backtest.analytics.report_models import (
    AdvancedMetricsReport,
    BacktestReportPack,
    PeriodicReturnReport,
)
from binance50.backtest.reports_v2 import (
    build_backtest_report_summary,
    build_breakdown_tables,
    build_drawdown_table,
    build_metrics_table,
    build_periodic_returns_table,
    build_report_health,
    build_trade_distribution_table,
)
from binance50.config.models import AppConfig


def test_build_backtest_report_summary():
    pack = BacktestReportPack(report_id="1", run_id="1", summary={"strategy": "test"})
    assert build_backtest_report_summary(pack) == {"strategy": "test"}


def test_build_metrics_table():
    metrics = AdvancedMetricsReport(run_id="1", cagr_pct=10.0, sharpe_ratio=1.5)
    pack = BacktestReportPack(report_id="1", run_id="1", advanced_metrics=metrics)
    table = build_metrics_table(pack)
    assert len(table) > 0
    cagr = next(item for item in table if item["metric"] == "cagr_pct")
    assert cagr["value"] == 10.0


def test_build_periodic_returns_table():
    pr = PeriodicReturnReport(run_id="1", frequency="daily", best_period={"return": 0.05})
    pack = BacktestReportPack(report_id="1", run_id="1", periodic_returns=[pr])
    table = build_periodic_returns_table(pack)
    assert len(table) == 1
    assert table[0]["frequency"] == "daily"
    assert table[0]["best_period"]["return"] == 0.05


def test_build_drawdown_table():
    pack = BacktestReportPack(report_id="1", run_id="1", drawdowns={"depth": 0.1})
    assert build_drawdown_table(pack) == {"depth": 0.1}


def test_build_trade_distribution_table():
    pack = BacktestReportPack(report_id="1", run_id="1", trade_distribution={"wins": 5})
    table = build_trade_distribution_table(pack)
    assert len(table) == 1
    assert table[0]["metric"] == "wins"
    assert table[0]["value"] == 5


def test_build_breakdown_tables():
    pack = BacktestReportPack(
        report_id="1", run_id="1", breakdowns={"regime": {"table": [{"bull": 5}]}}
    )
    tables = build_breakdown_tables(pack)
    assert "regime" in tables
    assert tables["regime"][0]["bull"] == 5


def test_build_report_health():
    config = AppConfig()
    health = build_report_health(config)
    assert health["status"] == "healthy"
    assert health["real_exchange_forbidden"] is True
