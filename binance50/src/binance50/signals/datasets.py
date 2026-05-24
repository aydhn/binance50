import pandas as pd

from binance50.signals.models import ConfluenceGroup, ScoredSignalCandidate
from binance50.signals.quality import SignalQualityReport


def scored_candidates_to_dataframe(scored: list[ScoredSignalCandidate]) -> pd.DataFrame:
    if not scored:
        return pd.DataFrame()

    data = []
    for s in scored:
        d = s.model_dump(mode="json")
        # Convert nested structures to strings for flat storage
        d["conflict_reasons_json"] = str(d.pop("conflict_reasons", []))
        d["score_breakdown_json"] = str(d.pop("score_breakdown", {}))
        d["explanation_json"] = d.pop("explanation", "")
        d["metadata_json"] = str(d.pop("metadata", {}))

        # Remove source candidate to avoid nesting
        d.pop("source_candidate", None)

        data.append(d)

    df = pd.DataFrame(data)

    # Ensure no execution columns
    from binance50.signals.validators import validate_no_execution_fields

    for col in df.columns:
        # Check field names
        try:
            validate_no_execution_fields({col: None})
        except Exception:
            df = df.drop(columns=[col])

    return df


def dataframe_to_scored_candidates(df: pd.DataFrame) -> list[ScoredSignalCandidate]:
    """Convert dataframe back to objects. Best effort string parsing."""
    import ast

    candidates = []
    records = df.to_dict(orient="records")

    for r in records:
        try:
            if "conflict_reasons_json" in r:
                r["conflict_reasons"] = ast.literal_eval(r.pop("conflict_reasons_json"))
            if "score_breakdown_json" in r:
                r["score_breakdown"] = ast.literal_eval(r.pop("score_breakdown_json"))
            if "explanation_json" in r:
                r["explanation"] = r.pop("explanation_json")
            if "metadata_json" in r:
                r["metadata"] = ast.literal_eval(r.pop("metadata_json"))

            candidates.append(ScoredSignalCandidate.model_validate(r))
        except Exception:
            pass  # Skip rows that fail to parse

    return candidates


def confluence_groups_to_dataframe(groups: list[ConfluenceGroup]) -> pd.DataFrame:
    if not groups:
        return pd.DataFrame()

    data = []
    for g in groups:
        d = g.model_dump(mode="json")
        d["plugin_names_str"] = ",".join(d.pop("plugin_names", []))
        d["plugin_types_str"] = ",".join(d.pop("plugin_types", []))
        d.pop("candidates", None)  # Remove raw candidates
        d["warnings_str"] = ",".join(d.pop("warnings", []))
        data.append(d)

    return pd.DataFrame(data)


def signal_quality_to_dataframe(report: SignalQualityReport) -> pd.DataFrame:
    if not report.issues:
        return pd.DataFrame()

    data = [i.model_dump(mode="json") for i in report.issues]
    return pd.DataFrame(data)
