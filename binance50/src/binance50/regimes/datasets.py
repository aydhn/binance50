import pandas as pd

from binance50.regimes.models import RegimeClassification


def regime_classifications_to_dataframe(
    classifications: list[RegimeClassification],
) -> pd.DataFrame:
    return pd.DataFrame([c.model_dump() for c in classifications])


def dataframe_to_regime_classifications(df: pd.DataFrame) -> list[RegimeClassification]:
    # Placeholder
    return []


def transitions_to_dataframe(transitions: list) -> pd.DataFrame:
    return pd.DataFrame([t.model_dump() for t in transitions])


def regime_quality_to_dataframe(report: Any) -> pd.DataFrame:
    # Placeholder
    return pd.DataFrame()
