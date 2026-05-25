import csv
import json
from pathlib import Path
from typing import Any

from binance50.optimizer.models import OptimizationRunResult, OptimizationTrial


def export_optimization_summary_to_json(result: OptimizationRunResult, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(result.model_dump(), f, indent=2)


def export_trials_to_csv(trials: list[OptimizationTrial], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not trials:
        return
    keys = trials[0].model_dump().keys()
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for t in trials:
            writer.writerow({k: str(v) for k, v in t.model_dump().items()})


def export_trials_to_jsonl(trials: list[OptimizationTrial], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for t in trials:
            f.write(json.dumps(t.model_dump()) + "\n")


def export_best_trial_to_json(trial: OptimizationTrial, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(trial.model_dump(), f, indent=2)


def export_overfit_report_to_json(result: OptimizationRunResult, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    reports = {t.trial_id: t.overfit_report for t in result.trials if t.overfit_report}
    with open(path, "w") as f:
        json.dump(reports, f, indent=2)


def export_robustness_report_to_json(result: OptimizationRunResult, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    reports = {t.trial_id: t.robustness_report for t in result.trials if t.robustness_report}
    with open(path, "w") as f:
        json.dump(reports, f, indent=2)


def export_search_space_to_json(specs: list[Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump([s.model_dump() for s in specs], f, indent=2)
