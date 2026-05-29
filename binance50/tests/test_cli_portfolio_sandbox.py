from typer.testing import CliRunner
from binance50.cli import app

runner = CliRunner()

def test_portfolio_sandbox_config_cli():
    result = runner.invoke(app, ["portfolio-sandbox-config"])
    assert result.exit_code == 0
    assert "Portfolio Sandbox Config" in result.stdout

def test_portfolio_run_selection_fixture_cli():
    result = runner.invoke(app, ["portfolio-run-selection-fixture", "--symbol", "BTCUSDT"])
    assert result.exit_code == 0
    assert "Running portfolio selection on fixture" in result.stdout
