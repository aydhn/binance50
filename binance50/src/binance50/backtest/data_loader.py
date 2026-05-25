import pandas as pd


class BacktestDataLoader:
    def load_from_fixture(
        self, fixture_name: str, symbol: str, market_scope: str, interval: str
    ) -> pd.DataFrame:
        # Stub implementation
        return pd.DataFrame()

    def load_from_market_data_cache(
        self, symbol: str, market_scope: str, interval: str
    ) -> pd.DataFrame:
        # Stub implementation
        return pd.DataFrame()

    def load_from_warehouse(
        self,
        symbol: str,
        market_scope: str,
        interval: str,
        start_time_ms: int | None = None,
        end_time_ms: int | None = None,
    ) -> pd.DataFrame:
        # Stub implementation
        return pd.DataFrame()

    def prepare_ohlcv_for_backtest(self, df: pd.DataFrame, config) -> pd.DataFrame:
        return df

    def validate_loaded_data(self, df: pd.DataFrame, config) -> None:
        pass

    def slice_date_range(
        self, df: pd.DataFrame, start_time_ms: int | None, end_time_ms: int | None
    ) -> pd.DataFrame:
        if start_time_ms is not None:
            df = df[df["open_time"] >= start_time_ms]
        if end_time_ms is not None:
            df = df[df["open_time"] <= end_time_ms]
        return df
