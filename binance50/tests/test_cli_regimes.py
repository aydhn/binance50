from typer.testing import CliRunner

from binance50.cli import app

runner = CliRunner()


def test_regime_config_cli():
    result = runner.invoke(app, ["regime-config"])
    assert result.exit_code == 0
    assert "Regime Configuration" in result.stdout


def test_regime_health_cli():
    result = runner.invoke(app, ["regime-health"])
    assert result.exit_code == 0
    assert "Regime Module Health" in result.stdout
