import json
from pathlib import Path

import pandas as pd

from binance50.indicators.models import IndicatorFrameMetadata
from binance50.indicators.quality import IndicatorQualityReport


def export_indicator_dataframe_to_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def export_indicator_dataframe_to_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path)


def export_indicator_metadata_to_json(metadata: IndicatorFrameMetadata, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(metadata.to_dict(), f, indent=2)


def export_indicator_quality_to_json(report: IndicatorQualityReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(report.to_dict(), f, indent=2)
