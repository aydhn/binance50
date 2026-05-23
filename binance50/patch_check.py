with open("scripts/check_project.py") as f:
    content = f.read()

phase9_checks = """
        (["python", "-m", "binance50.cli", "stream-config"], "Stream Config Check"),
        (["python", "-m", "binance50.cli", "stream-plan", "--symbols", "BTCUSDT,ETHUSDT", "--scope", "spot", "--types", "kline,bookTicker", "--interval", "1m"], "Stream Plan Check"),
        (["python", "-m", "binance50.cli", "stream-url-test", "--symbols", "BTCUSDT", "--scope", "spot", "--types", "kline", "--interval", "1m"], "Stream URL Test Check"),
        (["python", "-m", "binance50.cli", "stream-fixture-parse", "--fixture", "spot_kline_btcusdt_1m_closed.json", "--scope", "spot"], "Stream Fixture Parse Check"),
        (["python", "-m", "binance50.cli", "stream-simulate"], "Stream Simulate Check"),
        (["python", "-m", "binance50.cli", "stream-buffer-test"], "Stream Buffer Test Check"),
        (["python", "-m", "binance50.cli", "stream-replay-fixtures"], "Stream Replay Fixtures Check"),
        (["python", "-m", "binance50.cli", "stream-state-report"], "Stream State Report Check"),
        (["python", "-m", "binance50.cli", "stream-safety-check"], "Stream Safety Check"),
        (["python", "-m", "binance50.cli", "stream-health"], "Stream Health Check"),
"""

if "stream-config" not in content:
    content = content.replace(
        '(["python", "-m", "binance50.cli", "sdk-check"], "SDK Check"),',
        '(["python", "-m", "binance50.cli", "sdk-check"], "SDK Check"),\n' + phase9_checks,
    )
    with open("scripts/check_project.py", "w") as f:
        f.write(content)
