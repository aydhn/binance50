from pathlib import Path

file_path = Path("scripts/check_project.py")
content = file_path.read_text()

cli_checks = """
        (["python", "-m", "binance50.cli", "indicator-config"], "Indicator Config"),
        (["python", "-m", "binance50.cli", "indicator-backends"], "Indicator Backends"),
        (["python", "-m", "binance50.cli", "indicator-list"], "Indicator List"),
        (["python", "-m", "binance50.cli", "indicator-quality-check"], "Indicator Quality Check"),
        (["python", "-m", "binance50.cli", "indicator-safety-check"], "Indicator Safety Check"),
        (["python", "-m", "binance50.cli", "indicator-health"], "Indicator Health"),
"""

if "indicator-config" not in content:
    content = content.replace("cli_checks = [", "cli_checks = [\n" + cli_checks)

file_path.write_text(content)
print("Patched check_project.py")
