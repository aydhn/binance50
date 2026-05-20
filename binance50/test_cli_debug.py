from typer.testing import CliRunner

from binance50.cli import app

runner = CliRunner()
print("Starting rate limit simulate 429...")
result = runner.invoke(app, ["rate-limit-simulate", "429"])
print("Exit code:", result.exit_code)
print("Output:", result.stdout)
