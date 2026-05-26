import numpy as np
import pandas as pd
from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import MLFeatureSelectionError
from binance50.ml.datasets.models import MLFeatureColumnMetadata


class MLFeatureSelector:
    def select_features(self, df: pd.DataFrame, config: AppConfig) -> tuple[pd.DataFrame, list[MLFeatureColumnMetadata]]:
        df_filtered = self.exclude_forbidden_columns(df, config)
        self.validate_feature_columns(df_filtered, config)
        metadata = self.build_feature_metadata(df_filtered, config)
        return df_filtered, metadata

    def infer_feature_groups(self, columns: list[str]) -> dict[str, str]:
        groups = {}
        for col in columns:
            if col.startswith("trend_"):
                groups[col] = "trend"
            elif col.startswith("mom_"):
                groups[col] = "momentum"
            elif col.startswith("vol_"):
                groups[col] = "volatility"
            else:
                groups[col] = "other"
        return groups

    def exclude_forbidden_columns(self, df: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
        if not config.ml_dataset or not config.ml_dataset.feature_selection:
            return df

        exclude_prefixes = config.ml_dataset.feature_selection.exclude_prefixes
        forbidden_patterns = ["label_", "target_", "future_", "next_", "forward_", "order_", "execution_", "live_", "paper_", "testnet_", "api_key", "secret", "signature"]

        cols_to_keep = []
        for col in df.columns:
            is_forbidden = any(col.startswith(p) for p in exclude_prefixes) or any(p in col for p in forbidden_patterns)
            if not is_forbidden:
                cols_to_keep.append(col)

        return df[cols_to_keep]

    def validate_feature_columns(self, df: pd.DataFrame, config: AppConfig) -> None:
        if not config.ml_dataset or not config.ml_dataset.feature_selection:
            return

        fc = config.ml_dataset.feature_selection
        feature_cols = [c for c in df.columns if c not in fc.required_base_columns]

        if len(feature_cols) > fc.max_feature_columns:
            raise MLFeatureSelectionError(f"Exceeded max feature columns: {len(feature_cols)} > {fc.max_feature_columns}")

        if not fc.allow_object_features:
            for col in feature_cols:
                if df[col].dtype == 'object':
                    raise MLFeatureSelectionError(f"Object features not allowed: {col}")

    def detect_constant_features(self, df: pd.DataFrame) -> list[str]:
        constant_features = []
        for col in df.columns:
            if df[col].nunique(dropna=False) <= 1:
                constant_features.append(col)
        return constant_features

    def detect_high_nan_features(self, df: pd.DataFrame, config: AppConfig) -> list[str]:
        high_nan = []
        if not config.ml_dataset or not config.ml_dataset.feature_selection:
             return high_nan

        threshold = config.ml_dataset.feature_selection.max_nan_ratio_per_feature
        for col in df.columns:
            if df[col].isna().mean() > threshold:
                high_nan.append(col)
        return high_nan

    def detect_inf_features(self, df: pd.DataFrame) -> list[str]:
        inf_features = []
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                if np.isinf(df[col]).any():
                    inf_features.append(col)
        return inf_features

    def build_feature_metadata(self, df: pd.DataFrame, config: AppConfig) -> list[MLFeatureColumnMetadata]:
        metadata_list = []
        groups = self.infer_feature_groups(list(df.columns))
        constant_feats = self.detect_constant_features(df)
        high_nan_feats = self.detect_high_nan_features(df, config)
        inf_feats = self.detect_inf_features(df)

        for col in df.columns:
            warnings = []
            if col in constant_feats:
                warnings.append("constant_feature")
            if col in high_nan_feats:
                warnings.append("high_nan_ratio")
            if col in inf_feats:
                warnings.append("contains_inf")

            metadata = MLFeatureColumnMetadata(
                column_name=col,
                source="inferred",
                dtype=str(df[col].dtype),
                group=groups.get(col, "unknown"),
                nan_ratio=df[col].isna().mean(),
                inf_count=np.isinf(df[col]).sum() if pd.api.types.is_numeric_dtype(df[col]) else 0,
                constant=(col in constant_feats),
                warnings=warnings
            )
            metadata_list.append(metadata)
        return metadata_list
