from typer.testing import CliRunner

from binance50.cli import app

runner = CliRunner()


def test_strategy_config_command():
    result = runner.invoke(app, ["strategy-config"])
    assert result.exit_code == 0
    assert "execution_forbidden" in result.stdout


def test_strategy_list_command():
    result = runner.invoke(app, ["strategy-list"])
    assert result.exit_code == 0
    assert "trend_following" in result.stdout


def test_strategy_plugin_health_command():
    result = runner.invoke(app, ["strategy-plugin-health"])
    assert result.exit_code == 0
    assert "registry_health" not in result.stdout  # It just prints the registry.health_report
    assert "trend_following" in result.stdout


def test_strategy_safety_check_command():
    result = runner.invoke(app, ["strategy-safety-check"])
    assert result.exit_code == 0
    assert "config_safe" in result.stdout
    assert "true" in result.stdout.lower()


def test_strategy_health_command():
    result = runner.invoke(app, ["strategy-health"])
    assert result.exit_code == 0
    assert "config_safe" in result.stdout
