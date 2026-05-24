import json
from pathlib import Path

import pandas as pd

from binance50.regimes.models import RegimeClassification, RegimeRunResult


def export_regime_classifications_to_jsonl(
    classifications: list[RegimeClassification], path: str | Path
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for c in classifications:
            f.write(c.model_dump_json() + "\n")


def export_regime_classifications_to_csv(
    classifications: list[RegimeClassification], path: str | Path
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame([c.model_dump() for c in classifications])
    df.to_csv(path, index=False)


def export_regime_summary_to_json(result: RegimeRunResult, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        f.write(result.model_dump_json(indent=2))


def export_regime_transitions_to_json(transitions: list, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump([t.model_dump() for t in transitions], f, indent=2)
