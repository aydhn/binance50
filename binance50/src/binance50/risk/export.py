from pathlib import Path

from binance50.risk.datasets import risk_assessments_to_dataframe
from binance50.risk.models import RiskAssessment, RiskRunResult


def export_risk_assessments_to_jsonl(assessments: list[RiskAssessment], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for a in assessments:
            f.write(a.model_dump_json() + "\n")


def export_risk_assessments_to_csv(assessments: list[RiskAssessment], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df = risk_assessments_to_dataframe(assessments)
    df.to_csv(path, index=False)


def export_risk_summary_to_json(result: RiskRunResult, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        f.write(result.model_dump_json())


def export_risk_breakdown_to_json(assessment: RiskAssessment, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        f.write(assessment.breakdown.model_dump_json())
