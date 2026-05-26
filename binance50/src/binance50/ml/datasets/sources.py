import pandas as pd
from typing import Callable, Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import MLFeatureSourceError
from binance50.ml.datasets.models import MLFeatureSource

class MLFeatureSourceRegistry:
    def __init__(self):
        self._sources: dict[MLFeatureSource, Callable] = {}

    def register_source(self, name: MLFeatureSource, loader: Callable) -> None:
        self._sources[name] = loader

    def list_sources(self, enabled_only: bool = True) -> list[MLFeatureSource]:
        # For simplicity, returning all registered. In a real scenario, filter by config.
        return list(self._sources.keys())

    def load_source(self, source: MLFeatureSource, symbol: str, market_scope: str, interval: str, config: AppConfig) -> pd.DataFrame:
        if source not in self._sources:
            raise MLFeatureSourceError(f"Source {source} not registered")

        df = self._sources[source](symbol, market_scope, interval, config)
        self.validate_source_frame(source, df, config)
        return df

    def load_enabled_sources(self, symbol: str, market_scope: str, interval: str, config: AppConfig) -> dict[MLFeatureSource, pd.DataFrame]:
        enabled_sources = {}
        for source, loader in self._sources.items():
            try:
                # Add logic to check config if it's enabled. Assuming True for mock.
                df = self.load_source(source, symbol, market_scope, interval, config)
                enabled_sources[source] = df
            except Exception as e:
                # Log or handle depending on requirements
                pass
        return enabled_sources

    def validate_source_frame(self, source: MLFeatureSource, df: pd.DataFrame, config: AppConfig) -> None:
        if df is None or df.empty:
            raise MLFeatureSourceError(f"Source frame for {source} is empty")
        if 'open_time' not in df.columns:
            raise MLFeatureSourceError(f"Source frame for {source} missing open_time column")

    def build_source_report(self, sources: dict[MLFeatureSource, pd.DataFrame]) -> dict[str, Any]:
        return {str(name): len(df) for name, df in sources.items()}

# Built-in source loader skeletons
def load_indicator_v1_features(symbol: str, market_scope: str, interval: str, config: AppConfig) -> pd.DataFrame:
    df = pd.DataFrame({"open_time": [pd.Timestamp.now()]})
    return df

def load_indicator_v2_features(symbol: str, market_scope: str, interval: str, config: AppConfig) -> pd.DataFrame:
    df = pd.DataFrame({"open_time": [pd.Timestamp.now()]})
    return df

def load_scored_signal_features(symbol: str, market_scope: str, interval: str, config: AppConfig) -> pd.DataFrame:
    df = pd.DataFrame({"open_time": [pd.Timestamp.now()]})
    return df

def load_regime_features(symbol: str, market_scope: str, interval: str, config: AppConfig) -> pd.DataFrame:
    df = pd.DataFrame({"open_time": [pd.Timestamp.now()]})
    return df

def load_risk_assessment_features(symbol: str, market_scope: str, interval: str, config: AppConfig) -> pd.DataFrame:
    df = pd.DataFrame({"open_time": [pd.Timestamp.now()]})
    return df

def load_strategy_candidate_features(symbol: str, market_scope: str, interval: str, config: AppConfig) -> pd.DataFrame:
    df = pd.DataFrame({"open_time": [pd.Timestamp.now()]})
    return df

def load_backtest_metadata_features(symbol: str, market_scope: str, interval: str, config: AppConfig) -> pd.DataFrame:
    df = pd.DataFrame({"open_time": [pd.Timestamp.now()]})
    return df

def load_walkforward_metadata_features(symbol: str, market_scope: str, interval: str, config: AppConfig) -> pd.DataFrame:
    df = pd.DataFrame({"open_time": [pd.Timestamp.now()]})
    return df
