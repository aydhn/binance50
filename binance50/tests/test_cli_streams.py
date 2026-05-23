from typer.testing import CliRunner

from binance50.cli import app

runner = CliRunner()


def test_stream_config():
    result = runner.invoke(app, ["stream-config"])
    assert result.exit_code == 0
    assert "Stream Config" in result.stdout


def test_stream_plan():
    result = runner.invoke(
        app,
        [
            "stream-plan",
            "--symbols",
            "BTCUSDT",
            "--scope",
            "spot",
            "--types",
            "kline",
            "--interval",
            "1m",
        ],
    )
    assert result.exit_code == 0
    assert "Subscription Plan" in result.stdout


def test_stream_url_test():
    result = runner.invoke(
        app,
        [
            "stream-url-test",
            "--symbols",
            "BTCUSDT",
            "--scope",
            "spot",
            "--types",
            "kline",
            "--interval",
            "1m",
        ],
    )
    assert result.exit_code == 0
    assert "Full Stream URL" in result.stdout


def test_stream_simulate():
    result = runner.invoke(app, ["stream-simulate"])
    assert result.exit_code == 0
    assert "Simulation Result" in result.stdout


def test_stream_buffer_test():
    result = runner.invoke(app, ["stream-buffer-test"])
    assert result.exit_code == 0
    assert "Buffer Test" in result.stdout


def test_stream_health():
    result = runner.invoke(app, ["stream-health"])
    assert result.exit_code == 0
    assert "Stream Health" in result.stdout
