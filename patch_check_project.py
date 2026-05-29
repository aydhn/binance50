with open("binance50/scripts/check_project.py", "r") as f:
    content = f.read()

phase_26_checks = """
            (["python", "-m", "binance50.cli", "portfolio-sandbox-config"], "Portfolio Sandbox Config Check"),
            (["python", "-m", "binance50.cli", "portfolio-candidate-inputs"], "Portfolio Candidate Inputs Check"),
            (["python", "-m", "binance50.cli", "portfolio-run-selection-fixture", "--symbol", "BTCUSDT", "--scope", "spot", "--interval", "1m"], "Portfolio Fixture Selection Check"),
            (["python", "-m", "binance50.cli", "portfolio-selected-candidates"], "Portfolio Selected Candidates Check"),
            (["python", "-m", "binance50.cli", "portfolio-correlation-report"], "Portfolio Correlation Check"),
            (["python", "-m", "binance50.cli", "portfolio-exposure-report"], "Portfolio Exposure Check"),
            (["python", "-m", "binance50.cli", "portfolio-concentration-report"], "Portfolio Concentration Check"),
            (["python", "-m", "binance50.cli", "portfolio-diversification-report"], "Portfolio Diversification Check"),
            (["python", "-m", "binance50.cli", "portfolio-risk-budget-report"], "Portfolio Risk Budget Check"),
            (["python", "-m", "binance50.cli", "portfolio-safety-check"], "Portfolio Safety Guard Check"),
            (["python", "-m", "binance50.cli", "portfolio-integration-safety-check"], "Portfolio Integration Guard Check"),
"""

content = content.replace("    cli_checks.extend(", "    cli_checks.extend([\n" + phase_26_checks + "\n    ])\n    cli_checks.extend(")

with open("binance50/scripts/check_project.py", "w") as f:
    f.write(content)
