from typer.testing import CliRunner

from binance50.cli import app

runner = CliRunner()


def test_storage_config_command():
    result = runner.invoke(app, ["storage-config"])
    assert result.exit_code == 0
    assert "enabled" in result.stdout


def test_storage_health_command():
    result = runner.invoke(app, ["storage-health"])
    assert result.exit_code == 0
    assert "status" in result.stdout


def test_storage_safety_check_command():
    result = runner.invoke(app, ["storage-safety-check"])
    assert result.exit_code == 0
    assert "safe" in result.stdout
