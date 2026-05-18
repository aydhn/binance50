from typer.testing import CliRunner

from binance50.cli import app

runner = CliRunner()


def test_list_environments():
    result = runner.invoke(app, ["list-environments"])
    assert result.exit_code == 0
    assert "Environment Profiles" in result.stdout


def test_show_environment_default():
    result = runner.invoke(app, ["show-environment"])
    assert result.exit_code == 0
    assert "Environment Profile: local_paper_spot" in result.stdout
    assert "binance" in result.stdout


def test_show_environment_specific():
    result = runner.invoke(app, ["show-environment", "--profile", "spot_testnet"])
    assert result.exit_code == 0
    assert "Environment Profile: spot_testnet" in result.stdout
    assert "testnet.binance.vision" in result.stdout


def test_show_environment_invalid():
    result = runner.invoke(app, ["show-environment", "--profile", "invalid_profile"])
    assert result.exit_code == 1
    assert "not found in environment matrix" in result.stdout


def test_environment_safety_report_safe():
    result = runner.invoke(app, ["environment-safety-report"])
    assert result.exit_code == 0
    assert "safe: paper mode, real orders disabled" in result.stdout


def test_safety_check():
    result = runner.invoke(app, ["safety-check"])
    assert result.exit_code == 0
    assert "Environment Matrix Guard passed" in result.stdout
