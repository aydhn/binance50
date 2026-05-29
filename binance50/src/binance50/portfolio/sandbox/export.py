import json
from pathlib import Path

import pandas as pd

from binance50.portfolio.sandbox.models import PortfolioSelectionRunResult


def export_portfolio_selection_summary_to_json(
    result: PortfolioSelectionRunResult, path: Path
) -> Path:
    from binance50.portfolio.sandbox.reports import build_portfolio_selection_summary

    data = build_portfolio_selection_summary(result)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return path


def export_input_candidates_to_csv(candidates: list, path: Path) -> Path:
    from binance50.portfolio.sandbox.reports import build_input_candidate_table

    df = pd.DataFrame(build_input_candidate_table(candidates))
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


def export_selected_candidates_to_csv(candidates: list, path: Path) -> Path:
    from binance50.portfolio.sandbox.selection import selected_candidates_to_dataframe

    df = selected_candidates_to_dataframe(candidates)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


def export_selected_candidates_to_parquet(candidates: list, path: Path) -> Path:
    from binance50.portfolio.sandbox.selection import selected_candidates_to_dataframe

    df = selected_candidates_to_dataframe(candidates)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    return path


def export_correlation_matrix_to_csv(report: dict, path: Path) -> Path:
    # A bit complex because it's a dict, placeholder
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(report, f)
    return path


def export_exposure_report_to_json(report: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    return path


def export_concentration_report_to_json(report: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    return path


def export_diversification_report_to_json(report: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    return path


def export_quality_report_to_json(report: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    return path
