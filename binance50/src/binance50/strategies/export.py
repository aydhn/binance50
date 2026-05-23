import json
from pathlib import Path

from binance50.strategies.candidates import candidates_to_dataframe
from binance50.strategies.models import SignalCandidate, StrategyRunResult


def export_candidates_to_jsonl(candidates: list[SignalCandidate], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for c in candidates:
            f.write(json.dumps(c.model_dump()) + "\n")


def export_candidates_to_csv(candidates: list[SignalCandidate], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df = candidates_to_dataframe(candidates)
    if not df.empty:
        df.to_csv(path, index=False)


def export_strategy_summary_to_json(result: StrategyRunResult, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    from binance50.strategies.reports import build_strategy_run_summary

    with open(path, "w") as f:
        json.dump(build_strategy_run_summary(result), f, indent=2)


def export_plugin_reports_to_json(result: StrategyRunResult, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(result.plugin_reports, f, indent=2)
