from typer.testing import CliRunner

from binance50.cli import app

runner = CliRunner()


def test_cli_risk_config():
    result = runner.invoke(app, ["risk-config"])
    assert result.exit_code == 0
    assert "Risk Engine Configuration Summary" in result.stdout


def test_cli_risk_limit_report():
    result = runner.invoke(app, ["risk-limit-report"])
    assert result.exit_code == 0
    assert "global_limits" in result.stdout


def test_cli_risk_run_fixture():
    result = runner.invoke(app, ["risk-run-fixture"])
    assert result.exit_code == 0
    assert "Risk Assessment Preview" in result.stdout


def test_cli_risk_assessment_preview():
    result = runner.invoke(app, ["risk-assessment-preview"])
    assert result.exit_code == 0


def test_cli_risk_component_report():
    result = runner.invoke(app, ["risk-component-report"])
    assert result.exit_code == 0


def test_cli_risk_quality_check():
    result = runner.invoke(app, ["risk-quality-check"])
    assert result.exit_code == 0


def test_cli_risk_cache_list():
    result = runner.invoke(app, ["risk-cache-list"])
    assert result.exit_code == 0


def test_cli_risk_safety_check():
    result = runner.invoke(app, ["risk-safety-check"])
    assert result.exit_code == 0
    assert "execution_forbidden" in result.stdout


def test_cli_risk_execution_guard_check():
    result = runner.invoke(app, ["risk-execution-guard-check"])
    assert result.exit_code == 0
    assert "no_order_object_created" in result.stdout


def test_cli_risk_health():
    result = runner.invoke(app, ["risk-health"])
    assert result.exit_code == 0
    assert "config_enabled" in result.stdout
