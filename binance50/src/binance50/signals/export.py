import json
from pathlib import Path
from typing import Any

from binance50.signals.models import ConfluenceGroup, ScoredSignalCandidate, SignalScoringResult


def export_scored_signals_to_jsonl(scored: list[ScoredSignalCandidate], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for s in scored:
            f.write(json.dumps(s.model_dump(mode="json")) + "\n")


def export_scored_signals_to_csv(scored: list[ScoredSignalCandidate], path: Path) -> None:
    import pandas as pd
    from binance50.signals.datasets import scored_candidates_to_dataframe

    df = scored_candidates_to_dataframe(scored)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def export_signal_summary_to_json(result: SignalScoringResult, path: Path) -> None:
    from binance50.signals.reports import build_signal_run_summary

    summary = build_signal_run_summary(result)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(summary, f, indent=2)


def export_confluence_report_to_json(result: SignalScoringResult, path: Path) -> None:
    from binance50.signals.reports import build_confluence_group_report

    report = build_confluence_group_report(result.confluence_groups)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(report, f, indent=2)


def export_score_breakdown_to_json(scored: ScoredSignalCandidate, path: Path) -> None:
    from binance50.signals.reports import format_score_breakdown

    breakdown = format_score_breakdown(scored)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(breakdown, f, indent=2)
