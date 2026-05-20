from pathlib import Path

content = Path("binance50/tests/test_cli_environment.py").read_text()
# Remove test_safety_check since test_cli_safety_phase4.py already covers CLI tests better
content = content.replace(
'''def test_safety_check():
    result = runner.invoke(app, ["safety-check"])
    assert result.exit_code in (0, 1)
    assert "Environment Matrix Guard passed" in result.stdout''',
''
)
Path("binance50/tests/test_cli_environment.py").write_text(content)
