from typer.testing import CliRunner

from binance50.cli import app

runner = CliRunner()
print("Starting clock_sync_status...")
result = runner.invoke(app, ["clock-sync-status"])
print("Exit code:", result.exit_code)
print("Output:", result.stdout)
