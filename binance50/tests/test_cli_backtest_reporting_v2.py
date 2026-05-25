from typer.testing import CliRunner

from binance50.cli import app

runner = CliRunner()


def test_cli_backtest_reporting_config():
    result = runner.invoke(app, ["backtest-reporting-config"])
    assert result.exit_code == 0


def test_cli_backtest_report_pack():
    result = runner.invoke(app, ["backtest-report-pack"])
    assert result.exit_code == 0


def test_cli_backtest_advanced_metrics():
    result = runner.invoke(app, ["backtest-advanced-metrics"])
    assert result.exit_code == 0


def test_cli_backtest_rolling_metrics():
    result = runner.invoke(app, ["backtest-rolling-metrics"])
    assert result.exit_code == 0


def test_cli_backtest_periodic_returns():
    result = runner.invoke(app, ["backtest-periodic-returns"])
    assert result.exit_code == 0


def test_cli_backtest_monthly_returns():
    result = runner.invoke(app, ["backtest-monthly-returns"])
    assert result.exit_code == 0


def test_cli_backtest_benchmark_v2():
    result = runner.invoke(app, ["backtest-benchmark-v2"])
    assert result.exit_code == 0


def test_cli_backtest_drawdown_v2():
    result = runner.invoke(app, ["backtest-drawdown-v2"])
    assert result.exit_code == 0


def test_cli_backtest_trade_distribution():
    result = runner.invoke(app, ["backtest-trade-distribution"])
    assert result.exit_code == 0


def test_cli_backtest_holding_time():
    result = runner.invoke(app, ["backtest-holding-time"])
    assert result.exit_code == 0


def test_cli_backtest_regime_breakdown():
    result = runner.invoke(app, ["backtest-regime-breakdown"])
    assert result.exit_code == 0


def test_cli_backtest_signal_breakdown():
    result = runner.invoke(app, ["backtest-signal-breakdown"])
    assert result.exit_code == 0


def test_cli_backtest_cost_analysis():
    result = runner.invoke(app, ["backtest-cost-analysis"])
    assert result.exit_code == 0


def test_cli_backtest_exposure_analysis():
    result = runner.invoke(app, ["backtest-exposure-analysis"])
    assert result.exit_code == 0


def test_cli_backtest_report_quality_check():
    result = runner.invoke(app, ["backtest-report-quality-check"])
    assert result.exit_code == 0


def test_cli_backtest_report_export():
    result = runner.invoke(app, ["backtest-report-export"])
    assert result.exit_code == 0


def test_cli_backtest_reporting_safety_check():
    result = runner.invoke(app, ["backtest-reporting-safety-check"])
    assert result.exit_code == 0


def test_cli_backtest_metrics_safety_check():
    result = runner.invoke(app, ["backtest-metrics-safety-check"])
    assert result.exit_code == 0


def test_cli_backtest_reporting_health():
    result = runner.invoke(app, ["backtest-reporting-health"])
    assert result.exit_code == 0
