from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.regimes.adapters.base import RegimeModelAdapter


class GMMAdapter(RegimeModelAdapter):
    def __init__(self, config: AppConfig):
        self.config = config.regimes.optional_models["gmm"]
        self.is_installed = False
        try:
            import sklearn

            self.is_installed = True
        except ImportError:
            pass

    def name(self) -> str:
        return "gmm_optional"

    def is_available(self) -> bool:
        return self.is_installed and self.config.enabled

    def availability_report(self) -> dict[str, Any]:
        return {
            "name": self.name(),
            "installed": self.is_installed,
            "enabled": self.config.enabled,
            "available": self.is_available(),
        }

    def fit(self, train_df: pd.DataFrame, feature_columns: list[str]) -> None:
        if not self.config.require_train_split:
            raise ValueError("GMM fit requires train_split=True")
        pass

    def predict(self, df: pd.DataFrame) -> pd.Series:
        return pd.Series(0, index=df.index)

    def predict_proba(self, df: pd.DataFrame) -> pd.DataFrame | None:
        return None

    def map_clusters_to_regimes(self, df: pd.DataFrame, labels: pd.Series) -> dict[int, str]:
        return {0: "unknown"}

    def save_model(self, path: str) -> None:
        pass

    def load_model(self, path: str) -> None:
        pass
