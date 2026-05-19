import pytest
from typer.testing import CliRunner

from binance50.cli import app
from binance50.logging.setup import shutdown_logging

runner = CliRunner()


@pytest.fixture(autouse=True)
def cleanup_logging():
    yield
    shutdown_logging()


def test_log_test_command():
    result = runner.invoke(app, ["log-test"])
    assert result.exit_code == 0
    assert "Log test complete" in result.stdout


def test_audit_test_command():
    result = runner.invoke(app, ["audit-test"])
    assert result.exit_code == 0
    assert "Audit test complete" in result.stdout


def test_error_test_command():
    result = runner.invoke(app, ["error-test"])
    assert result.exit_code == 0
    assert "Error test complete" in result.stdout


def test_doctor_command():
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "Binance50 Doctor" in result.stdout
    assert "Passed" in result.stdout
