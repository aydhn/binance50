import pytest
from binance50.cli import app
from typer.testing import CliRunner

runner = CliRunner()

def test_signal_config():
    result = runner.invoke(app, ["signal-config", "--config-dir", "config"])
    assert result.exit_code == 0
    assert "execution_forbidden" in result.stdout

def test_signal_thresholds():
    result = runner.invoke(app, ["signal-thresholds", "--config-dir", "config"])
    assert result.exit_code == 0
    assert "no_action_below" in result.stdout

def test_signal_weight_report():
    result = runner.invoke(app, ["signal-weight-report", "--config-dir", "config"])
    assert result.exit_code == 0
    assert "plugin_weights" in result.stdout

def test_signal_run_fixture():
    result = runner.invoke(app, ["signal-run-fixture", "--config-dir", "config"])
    assert result.exit_code == 0
    assert "NO ORDERS GENERATED" in result.stdout

def test_signal_score_preview():
    result = runner.invoke(app, ["signal-score-preview"])
    assert result.exit_code == 0
    assert "Previewing scored signal candidates" in result.stdout

def test_signal_confluence_report():
    result = runner.invoke(app, ["signal-confluence-report"])
    assert result.exit_code == 0
    assert "Confluence group summary report" in result.stdout

def test_signal_conflict_report():
    result = runner.invoke(app, ["signal-conflict-report"])
    assert result.exit_code == 0
    assert "Conflict summary report" in result.stdout

def test_signal_calibration_report():
    result = runner.invoke(app, ["signal-calibration-report", "--config-dir", "config"])
    assert result.exit_code == 0
    assert "placeholder_metrics_only" in result.stdout

def test_signal_quality_check():
    result = runner.invoke(app, ["signal-quality-check"])
    assert result.exit_code == 0
    assert "Signal quality checked" in result.stdout

def test_signal_cache_list():
    result = runner.invoke(app, ["signal-cache-list", "--config-dir", "config"])
    assert result.exit_code == 0

def test_signal_safety_check():
    result = runner.invoke(app, ["signal-safety-check", "--config-dir", "config"])
    assert result.exit_code == 0
    assert "scoring_safety" in result.stdout

def test_signal_health():
    result = runner.invoke(app, ["signal-health", "--config-dir", "config"])
    assert result.exit_code == 0
    assert "execution_forbidden" in result.stdout
