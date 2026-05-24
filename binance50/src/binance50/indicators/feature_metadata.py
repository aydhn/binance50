import uuid
from datetime import UTC, datetime

import pandas as pd
from pydantic import BaseModel

from binance50.config.models import AppConfig
from binance50.core.exceptions import FeatureMetadataError
from binance50.features.grouping import exclude_non_feature_columns

from .feature_groups import infer_feature_group


class FeatureMetadata(BaseModel):
    feature_name: str
    group: str | None
    source: str
    input_columns: list[str] = []
    parameters: dict = {}
    lookback: int = 0
    timeframe: str = ""
    is_mtf: bool = False
    is_divergence: bool = False
    is_pattern: bool = False
    is_safe_for_training: bool = False
    is_safe_for_backtest: bool = False
    warmup_rows: int = 0
    nan_ratio: float = 0.0
    created_at_utc: datetime
    warnings: list[str] = []


class FeatureSetMetadata(BaseModel):
    feature_set_id: str
    symbol: str
    market_scope: str
    base_interval: str
    feature_count: int
    groups: list[str]
    features: list[FeatureMetadata]
    input_hashes: dict[str, str] = {}
    output_hash: str = ""
    config_hash: str = ""
    generated_at_utc: datetime
    quality_status: str = "pending"
    warnings: list[str] = []


def build_feature_metadata_for_columns(
    df: pd.DataFrame, config: AppConfig
) -> list[FeatureMetadata]:
    features = exclude_non_feature_columns(df.columns.tolist())
    metadata_list = []
    now = datetime.now(UTC)

    # Calculate nan ratios
    total_rows = len(df)
    nan_counts = df[features].isna().sum() if total_rows > 0 else pd.Series(0, index=features)

    for col in features:
        group = infer_feature_group(col, config)
        is_mtf = col.startswith("mtf_")
        is_div = col.startswith("div_")
        is_pat = col.startswith("pat_")

        nan_ratio = float(nan_counts[col] / total_rows) if total_rows > 0 else 0.0

        meta = FeatureMetadata(
            feature_name=col,
            group=group,
            source="indicator_v2_engine",
            is_mtf=is_mtf,
            is_divergence=is_div,
            is_pattern=is_pat,
            is_safe_for_training=True,  # Will be verified by guards later
            is_safe_for_backtest=True,
            nan_ratio=nan_ratio,
            created_at_utc=now,
        )
        metadata_list.append(meta)

    return metadata_list


def build_feature_set_metadata(
    df: pd.DataFrame,
    config: AppConfig,
    input_hashes: dict[str, str],
    config_hash: str,
    output_hash: str,
) -> FeatureSetMetadata:
    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "unknown"
    market_scope = df["market_scope"].iloc[0] if "market_scope" in df.columns else "unknown"
    interval = df["interval"].iloc[0] if "interval" in df.columns else "unknown"

    features = build_feature_metadata_for_columns(df, config)
    groups = list({f.group for f in features if f.group})

    return FeatureSetMetadata(
        feature_set_id=uuid.uuid4().hex,
        symbol=symbol,
        market_scope=market_scope,
        base_interval=interval,
        feature_count=len(features),
        groups=groups,
        features=features,
        input_hashes=input_hashes,
        output_hash=output_hash,
        config_hash=config_hash,
        generated_at_utc=datetime.now(UTC),
    )


def feature_metadata_to_dataframe(metadata: list[FeatureMetadata]) -> pd.DataFrame:
    if not metadata:
        return pd.DataFrame()
    return pd.DataFrame([m.model_dump() for m in metadata])


def validate_feature_metadata(metadata: FeatureMetadata) -> None:
    from binance50.features.grouping import TARGET_KEYWORDS

    col_lower = metadata.feature_name.lower()
    if any(k in col_lower for k in TARGET_KEYWORDS):
        raise FeatureMetadataError(
            f"Target/label/future keyword found in feature name: {metadata.feature_name}"
        )

    if metadata.nan_ratio > 0.99:
        metadata.warnings.append("Extremely high NaN ratio")
