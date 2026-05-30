from typer.testing import CliRunner
from binance50.cli import app

runner = CliRunner()

def test_execution_config():
    result = runner.invoke(app, ["execution-config"])
    assert result.exit_code == 0, result.stdout
    assert "default_mode" in result.stdout

def test_execution_modes():
    result = runner.invoke(app, ["execution-modes"])
    assert result.exit_code == 0, result.stdout

def test_execution_run_safety_fixture():
    result = runner.invoke(app, ["execution-run-safety-fixture"])
    assert result.exit_code == 0, result.stdout
    assert "Passed" in result.stdout
