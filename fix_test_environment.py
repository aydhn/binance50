from pathlib import Path
content = Path("binance50/tests/test_environment_matrix.py").read_text()
content = content.replace('assert report["safety_status"] == "safe: paper mode, real orders disabled"', 'assert report["safety_status"] == "safe"')
content = content.replace('monkeypatch.setenv("BINANCE50_CONFIRM_LIVE_TRADING", "true")', 'monkeypatch.setenv("BINANCE50_CONFIRM_LIVE_TRADING", "true")\n    monkeypatch.setenv("BINANCE50_FORCE_PAPER_MODE", "false")\n    monkeypatch.setenv("BINANCE50_DRY_RUN", "false")')
Path("binance50/tests/test_environment_matrix.py").write_text(content)
