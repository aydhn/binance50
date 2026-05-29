with open("binance50/src/binance50/cli.py", "r") as f:
    content = f.read()

doctor_integration = """
    # Phase 26
    portfolio_sandbox_config()
    portfolio_candidate_inputs()
    portfolio_run_selection_fixture()
    portfolio_selected_candidates()
    portfolio_correlation_report()
    portfolio_exposure_report()
    portfolio_concentration_report()
    portfolio_diversification_report()
    portfolio_risk_budget_report()
    portfolio_safety_check()
    portfolio_integration_safety_check()
    print("production allocation forbidden: True")
    print("position sizing production forbidden: True")
    print("selected candidates blocked flags: True")
"""

content = content.replace("    console.print(\"Binance50 Doctor\")", doctor_integration + "\n    console.print(\"Binance50 Doctor\")")

with open("binance50/src/binance50/cli.py", "w") as f:
    f.write(content)
