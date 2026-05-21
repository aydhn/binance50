import json
from pathlib import Path

import pandas as pd

from binance50.config.models import AppConfig
from binance50.core.enums import MarketScope
from binance50.core.exceptions import OHLCVParseError
from binance50.market_data.kline_parser import bars_to_dataframe, parse_kline_payload
from binance50.market_data.ohlcv_models import OHLCVFetchResult, OHLCVSource


def get_fixture_path(name: str) -> Path:
    # Assuming fixtures are in src/binance50/data/fixtures
    base_dir = Path(__file__).parent.parent / "data" / "fixtures"
    return base_dir / name


def load_ohlcv_fixture(
    name: str, symbol: str, market_scope: MarketScope, interval: str
) -> pd.DataFrame:
    path = get_fixture_path(name)
    if not path.exists():
        raise FileNotFoundError(f"Fixture {name} not found at {path}")

    try:
        with open(path) as f:
            payload = json.load(f)
    except json.JSONDecodeError as e:
        raise OHLCVParseError(f"Failed to parse fixture JSON {name}: {e}")

    if not isinstance(payload, list):
        raise OHLCVParseError(f"Fixture payload {name} must be a list")

    bars = parse_kline_payload(
        payload=payload,
        symbol=symbol,
        market_scope=market_scope,
        interval=interval,
        source=OHLCVSource.FIXTURE,
    )

    return bars_to_dataframe(bars)


def load_fixture_fetch_result(
    name: str, symbol: str, market_scope: MarketScope, interval: str, config: AppConfig
) -> OHLCVFetchResult:
    from binance50.connectors.rest_client import BinanceRestClient
    from binance50.market_data.fetcher import OHLCVFetcher

    # Just a mock client to pass to fetcher
    client = BinanceRestClient(config, None, None, None)
    fetcher = OHLCVFetcher(config, client)

    path = get_fixture_path(name)
    return fetcher.fetch_from_fixture(path, symbol, market_scope, interval)


def list_ohlcv_fixtures() -> list[str]:
    base_dir = Path(__file__).parent.parent / "data" / "fixtures"
    if not base_dir.exists():
        return []

    return [f.name for f in base_dir.glob("ohlcv_*.json")]
