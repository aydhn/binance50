from typer.testing import CliRunner

from binance50.cli import app

runner = CliRunner()


def test_cli_rate_limit_status():
    result = runner.invoke(app, ["rate-limit-status"])
    assert result.exit_code == 0
    assert "status" in result.stdout


def test_cli_rate_limit_simulate_429():
    result = runner.invoke(app, ["rate-limit-simulate", "429"])
    assert result.exit_code == 0
    assert "False" in result.stdout
    assert "cooldown" in result.stdout


def test_cli_rate_limit_simulate_418():
    result = runner.invoke(app, ["rate-limit-simulate", "418"])
    assert result.exit_code == 0
    assert "False" in result.stdout
    assert "banned" in result.stdout or "hard_stop=True" in result.stdout


def test_cli_retry_policy_show():
    result = runner.invoke(app, ["retry-policy-show"])
    assert result.exit_code == 0


def test_cli_backoff_test():
    result = runner.invoke(app, ["backoff-test", "500", "2"])
    assert result.exit_code == 0
    assert "delay_seconds" in result.stdout


def test_cli_timeout_policy_show():
    result = runner.invoke(app, ["timeout-policy-show"])
    assert result.exit_code == 0


def test_cli_recv_window_check():
    result = runner.invoke(app, ["recv-window-check"])
    assert result.exit_code == 0
    assert "valid" in result.stdout


def test_cli_clock_sync_status():
    result = runner.invoke(app, ["clock-sync-status"])
    assert result.exit_code == 0


def test_cli_clock_sync_simulate():
    result = runner.invoke(app, ["clock-sync-simulate", "1000", "500", "1500"])
    assert result.exit_code == 0
    assert "offset" in result.stdout


def test_cli_websocket_limits_check():
    result = runner.invoke(app, ["websocket-limits-check", "spot", "1024", "2"])
    assert result.exit_code == 0
    assert "Stream check" in result.stdout


def test_cli_network_safety_report():
    result = runner.invoke(app, ["network-safety-report"])
    assert result.exit_code == 0
    assert "config_safe': True" in result.stdout
