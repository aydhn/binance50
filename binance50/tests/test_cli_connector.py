from typer.testing import CliRunner

from binance50.cli import app

runner = CliRunner()


def test_connector_status() -> None:
    result = runner.invoke(app, ["connector-status"])
    assert result.exit_code == 0
    assert "Selected Adapter" in result.stdout
    assert "REST Enabled" in result.stdout


def test_connector_health() -> None:
    result = runner.invoke(app, ["connector-health"])
    assert result.exit_code == 0
    assert "disabled_safe" in result.stdout


def test_connector_endpoints() -> None:
    result = runner.invoke(app, ["connector-endpoints"])
    assert result.exit_code == 0
    assert "local_paper_spot" in result.stdout


def test_connector_capabilities() -> None:
    result = runner.invoke(app, ["connector-capabilities"])
    assert result.exit_code == 0
    assert "supports_rest" in result.stdout


def test_connector_stream_url_test() -> None:
    result = runner.invoke(
        app,
        [
            "connector-stream-url-test",
            "--symbol",
            "BTCUSDT",
            "--stream",
            "kline",
            "--interval",
            "1m",
        ],
    )
    assert result.exit_code == 0
    assert "btcusdt@kline_1m" in result.stdout


def test_sdk_check() -> None:
    result = runner.invoke(app, ["sdk-check"])
    assert result.exit_code == 0
    assert "spot_sdk" in result.stdout
