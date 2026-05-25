import csv
import json
from pathlib import Path
from typing import Any

from binance50.backtest.analytics.report_models import BacktestReportPack
from binance50.backtest.reports_v2 import (
    build_backtest_report_summary,
    build_drawdown_table,
    build_metrics_table,
    build_periodic_returns_table,
    build_trade_distribution_table,
)


def export_report_pack_to_json(pack: BacktestReportPack, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        # Convert datetime to string in dump
        dump = pack.model_dump()
        dump["generated_at_utc"] = str(dump["generated_at_utc"])
        json.dump(dump, f, indent=2)
    return path


def export_report_pack_to_markdown(pack: BacktestReportPack, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    summary = build_backtest_report_summary(pack)

    with open(path, "w") as f:
        f.write(f"# Backtest Report: {pack.report_id}\n\n")
        f.write("## Summary\n")
        for k, v in summary.items():
            f.write(f"- **{k}**: {v}\n")

        f.write("\n## Disclaimer\n")
        f.write(f"_{pack.disclaimer}_\n")

        f.write(f"\nHash: `{pack.report_hash}`\n")
    return path


def _export_table_to_csv(table: list[dict[str, Any]], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not table:
        with open(path, "w") as f:
            f.write("")
        return path

    keys = list(table[0].keys())
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(table)
    return path


def export_metrics_to_csv(pack: BacktestReportPack, path: Path) -> Path:
    table = build_metrics_table(pack)
    return _export_table_to_csv(table, path)


def export_periodic_returns_to_csv(pack: BacktestReportPack, path: Path) -> Path:
    table = build_periodic_returns_table(pack)
    return _export_table_to_csv(table, path)


def export_drawdowns_to_csv(pack: BacktestReportPack, path: Path) -> Path:
    table = build_drawdown_table(pack)
    return _export_table_to_csv(table, path)


def export_trade_distribution_to_csv(pack: BacktestReportPack, path: Path) -> Path:
    table = build_trade_distribution_table(pack)
    return _export_table_to_csv(table, path)


def export_static_html_skeleton(pack: BacktestReportPack, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Backtest Report {pack.report_id}</title>
</head>
<body>
    <h1>Backtest Report</h1>
    <p>{pack.disclaimer}</p>
    <p>Hash: {pack.report_hash}</p>
    <!-- Add more static content as needed -->
</body>
</html>"""
    with open(path, "w") as f:
        f.write(html)
    return path
