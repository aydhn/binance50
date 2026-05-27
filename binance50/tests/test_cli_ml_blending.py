import pytest
from typer.testing import CliRunner
from binance50.cli import app

runner = CliRunner()

def test_ml_blending_config():
    result = runner.invoke(app, ["ml-blending-config"])
    assert result.exit_code == 0

def test_ml_blending_health():
    result = runner.invoke(app, ["ml-blending-health"])
    assert result.exit_code == 0

def test_ml_run_blending_fixture():
    result = runner.invoke(app, ["ml-run-blending-fixture"])
    assert result.exit_code == 0
