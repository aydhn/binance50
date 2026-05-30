import re

with open("binance50/src/binance50/storage/schemas.py", "r") as f:
    content = f.read()

# Add to DatasetKind
if "paper_execution_runs" not in content:
    content = content.replace(
        "    execution_safety_runs = \"execution_safety_runs\"",
        "    execution_safety_runs = \"execution_safety_runs\"\n    paper_execution_runs = \"paper_execution_runs\"\n    paper_orders = \"paper_orders\"\n    paper_fills = \"paper_fills\"\n    paper_ledger_events = \"paper_ledger_events\"\n    paper_balance_snapshots = \"paper_balance_snapshots\"\n    paper_positions = \"paper_positions\"\n    paper_pnl_reports = \"paper_pnl_reports\"\n    paper_execution_events = \"paper_execution_events\"\n    paper_audit_events = \"paper_audit_events\"\n    paper_quality_reports = \"paper_quality_reports\""
    )

with open("binance50/src/binance50/storage/schemas.py", "w") as f:
    f.write(content)
