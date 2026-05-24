import json

import pandas as pd

from binance50.risk.models import (
    RiskAssessment,
    RiskAssessmentStatus,
    RiskIntent,
    RiskQualityReport,
)


def risk_assessments_to_dataframe(assessments: list[RiskAssessment]) -> pd.DataFrame:
    data = []
    for a in assessments:
        row = a.model_dump()
        row["breakdown_json"] = json.dumps(row.pop("breakdown", {}))
        row["regime_context_json"] = json.dumps(row.pop("regime_context", {}))
        row["signal_snapshot_json"] = json.dumps(row.pop("signal_snapshot", {}))
        row["metadata_json"] = json.dumps(row.pop("metadata", {}))
        data.append(row)
    return pd.DataFrame(data)


def dataframe_to_risk_assessments(df: pd.DataFrame) -> list[RiskAssessment]:
    assessments = []
    for _, row in df.iterrows():
        d = row.to_dict()
        if "breakdown_json" in d and d["breakdown_json"]:
            d["breakdown"] = json.loads(d.pop("breakdown_json"))
        if "regime_context_json" in d and pd.notna(d["regime_context_json"]):
            d["regime_context"] = json.loads(d.pop("regime_context_json"))
        else:
            d["regime_context"] = None
            if "regime_context_json" in d:
                del d["regime_context_json"]
        if "signal_snapshot_json" in d and pd.notna(d["signal_snapshot_json"]):
            d["signal_snapshot"] = json.loads(d.pop("signal_snapshot_json"))
        else:
            d["signal_snapshot"] = None
            if "signal_snapshot_json" in d:
                del d["signal_snapshot_json"]
        if "metadata_json" in d and pd.notna(d["metadata_json"]):
            d["metadata"] = json.loads(d.pop("metadata_json"))
        else:
            d["metadata"] = {}
            if "metadata_json" in d:
                del d["metadata_json"]
        if "status" in d and isinstance(d["status"], str):
            d["status"] = RiskAssessmentStatus(d["status"])
        if "intent" in d and isinstance(d["intent"], str):
            d["intent"] = RiskIntent(d["intent"])
        assessments.append(RiskAssessment(**d))
    return assessments


def risk_quality_to_dataframe(report: RiskQualityReport) -> pd.DataFrame:
    data = []
    for issue in report.issues:
        data.append(issue.model_dump())
    return pd.DataFrame(data)
