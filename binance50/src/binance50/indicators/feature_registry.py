import pandas as pd
from typing import Dict, List, Optional
from binance50.config.models import AppConfig
from binance50.core.exceptions import FeatureRegistryError
from .feature_metadata import FeatureMetadata, FeatureSetMetadata
from binance50.features.grouping import exclude_non_feature_columns

class FeatureRegistry:
    def __init__(self, config: AppConfig):
        self.config = config
        self._features: Dict[str, FeatureMetadata] = {}
        self._feature_sets: Dict[str, FeatureSetMetadata] = {}

    def register_feature(self, metadata: FeatureMetadata) -> None:
        if metadata.feature_name in self._features:
            raise FeatureRegistryError(f"Feature {metadata.feature_name} already registered")
        self._features[metadata.feature_name] = metadata

    def register_feature_set(self, metadata: FeatureSetMetadata) -> None:
        if metadata.feature_set_id in self._feature_sets:
            raise FeatureRegistryError(f"Feature set {metadata.feature_set_id} already registered")
        self._feature_sets[metadata.feature_set_id] = metadata

        for f_meta in metadata.features:
            try:
                self.register_feature(f_meta)
            except FeatureRegistryError:
                # If doing multiple passes, might already exist, update it
                self._features[f_meta.feature_name] = f_meta

    def get_feature(self, name: str) -> Optional[FeatureMetadata]:
        return self._features.get(name)

    def list_features(self, group: Optional[str] = None) -> List[FeatureMetadata]:
        if group:
            return [f for f in self._features.values() if f.group == group]
        return list(self._features.values())

    def list_feature_sets(self) -> List[FeatureSetMetadata]:
        return list(self._feature_sets.values())

    def validate_dataframe_features(self, df: pd.DataFrame, config: AppConfig) -> None:
        cfg = config.indicator_v2.quality

        features = exclude_non_feature_columns(df.columns.tolist())
        unregistered = []

        for f in features:
            if f not in self._features:
                unregistered.append(f)

        if unregistered and cfg.reject_unregistered_feature:
            raise FeatureRegistryError(f"Found {len(unregistered)} unregistered features. First few: {unregistered[:5]}")

    def to_report(self) -> dict:
        return {
            "total_features": len(self._features),
            "total_feature_sets": len(self._feature_sets),
            "groups": list(set(f.group for f in self._features.values() if f.group)),
            "is_safe": True
        }
