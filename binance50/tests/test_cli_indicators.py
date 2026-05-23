from typer.testing import CliRunner

from binance50.cli import app

runner = CliRunner()


def test_indicator_config():
    result = runner.invoke(app, ["indicator-config"])
    assert result.exit_code == 0


def test_indicator_backends():
    result = runner.invoke(app, ["indicator-backends"])
    assert result.exit_code == 0


def test_indicator_list():
    result = runner.invoke(app, ["indicator-list"])
    assert result.exit_code == 0


def test_indicator_quality_check():
    result = runner.invoke(app, ["indicator-quality-check"])
    assert result.exit_code == 0


def test_indicator_safety_check():
    result = runner.invoke(app, ["indicator-safety-check"])
    assert result.exit_code == 0


def test_indicator_health():
    result = runner.invoke(app, ["indicator-health"])
    assert result.exit_code == 0
