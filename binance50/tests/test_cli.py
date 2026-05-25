def test_backtest_cli_commands():
    from typer.testing import CliRunner

    from binance50.cli import app

    runner = CliRunner()
    commands = [
        "backtest-config",
        "backtest-run-fixture",
        "backtest-summary",
        "backtest-trades-report",
        "backtest-equity-report",
        "backtest-drawdown-report",
        "backtest-metrics-report",
        "backtest-benchmark-report",
        "backtest-timeline-report",
        "backtest-quality-check",
        "backtest-cache-list",
        "backtest-safety-check",
        "backtest-leakage-check",
        "backtest-execution-guard-check",
        "backtest-health",
    ]
    for cmd in commands:
        result = runner.invoke(app, [cmd])
        assert result.exit_code == 0
