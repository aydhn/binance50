from pathlib import Path

import pandas as pd


def export_ohlcv_to_csv(df: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


def export_ohlcv_to_jsonl(df: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_json(path, orient="records", lines=True)
    return path


def export_ohlcv_preview(df: pd.DataFrame, path: Path, rows: int = 100) -> Path:
    if df.empty:
        return export_ohlcv_to_csv(df, path)

    preview_df = df.head(rows)
    return export_ohlcv_to_csv(preview_df, path)
