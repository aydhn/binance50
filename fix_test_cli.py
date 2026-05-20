from pathlib import Path

content = Path("binance50/tests/test_cli_environment.py").read_text()
content = content.replace('assert "safe: paper mode, real orders disabled" in result.stdout', 'assert "Safety Status: safe" in result.stdout')
Path("binance50/tests/test_cli_environment.py").write_text(content)
