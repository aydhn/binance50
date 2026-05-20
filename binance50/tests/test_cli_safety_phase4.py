from typer.testing import CliRunner

from binance50.cli import app

runner = CliRunner()


def test_secrets_check_runs(monkeypatch, tmp_path):
    # Mock _get_repo_root to avoid looking for .env.example in real project root if it fails
    # But for CLI tests, let's just let it run against the current codebase as that's safe
    result = runner.invoke(app, ["secrets-check"])
    assert result.exit_code in (0, 1)  # Depends on environment, just ensure it doesn't crash
    assert "Secrets Check" in result.stdout


def test_api_key_check_runs():
    result = runner.invoke(app, ["api-key-check"])
    assert result.exit_code in (0, 1)
    assert "API Key Check" in result.stdout


def test_dry_run_check_runs():
    result = runner.invoke(app, ["dry-run-check"])
    assert result.exit_code in (0, 1)
    assert "Dry Run Check" in result.stdout


def test_live_unlock_check_runs():
    result = runner.invoke(app, ["live-unlock-check"])
    assert result.exit_code == 0  # Default is blocked as expected
    assert "Live Unlock Check" in result.stdout


def test_doctor_runs():
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "Binance50 Doctor" in result.stdout
    assert ".env.example Safety" in result.stdout
