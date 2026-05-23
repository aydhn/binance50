import pandas as pd
import pytest

from binance50.core.exceptions import StorageSchemaError
from binance50.storage.schemas import (
    get_ohlcv_schema,
    schema_to_pyarrow,
    validate_dataframe_schema,
)


def test_ohlcv_schema():
    schema = get_ohlcv_schema()
    assert schema.dataset_name == "ohlcv"
    assert "market_scope" in schema.primary_keys


def test_schema_to_pyarrow():
    schema = get_ohlcv_schema()
    pa_schema = schema_to_pyarrow(schema)
    assert pa_schema is not None
    assert "open_time" in pa_schema.names


def test_validate_dataframe_schema():
    schema = get_ohlcv_schema()
    df = pd.DataFrame(
        {
            "market_scope": ["spot"],
            "symbol": ["BTCUSDT"],
            "interval": ["1m"],
            "open_time": [1000],
            "open": [1.0],
            "high": [2.0],
            "low": [0.5],
            "close": [1.5],
            "volume": [100.0],
            "close_time": [2000],
            "quote_asset_volume": [150.0],
            "number_of_trades": [10],
            "taker_buy_base_asset_volume": [50.0],
            "taker_buy_quote_asset_volume": [75.0],
        }
    )

    # Should pass
    validate_dataframe_schema(df, schema)

    # Missing required
    df_missing = df.drop(columns=["open"])
    with pytest.raises(StorageSchemaError):
        validate_dataframe_schema(df_missing, schema)

    # Extra columns
    df_extra = df.copy()
    df_extra["extra"] = "test"
    with pytest.raises(StorageSchemaError):
        validate_dataframe_schema(df_extra, schema)

    # Secret column
    df_secret = df.copy()
    df_secret["my_secret_token"] = "123"
    with pytest.raises(StorageSchemaError):
        validate_dataframe_schema(df_secret, schema)
