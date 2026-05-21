from decimal import Decimal, InvalidOperation
from typing import Any

import pandas as pd

from binance50.core.enums import MarketScope
from binance50.core.exceptions import OHLCVParseError, OHLCVValidationError
from binance50.market_data.ohlcv_models import OHLCVBar, OHLCVSource

EXPECTED_COLUMNS = [
    "symbol",
    "market_scope",
    "interval",
    "open_time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "close_time",
    "quote_asset_volume",
    "number_of_trades",
    "taker_buy_base_volume",
    "taker_buy_quote_volume",
    "source",
    "is_closed",
]


def parse_kline_row(
    row: list[Any], symbol: str, market_scope: MarketScope, interval: str, source: OHLCVSource
) -> OHLCVBar:
    if not isinstance(row, list) or len(row) < 11:
        raise OHLCVParseError(
            f"Invalid kline row format. Expected at least 11 elements, got {len(row) if isinstance(row, list) else type(row)}"
        )

    try:
        open_time = int(row[0])
        close_time = int(row[6])
        number_of_trades = int(row[8])

        o = Decimal(str(row[1]))
        h = Decimal(str(row[2]))
        l = Decimal(str(row[3]))
        c = Decimal(str(row[4]))
        v = Decimal(str(row[5]))
        qav = Decimal(str(row[7]))
        tbbv = Decimal(str(row[9]))
        tbqv = Decimal(str(row[10]))

    except (ValueError, TypeError, InvalidOperation) as e:
        raise OHLCVValidationError(f"Failed to parse numeric values from row: {e}")

    if h < l:
        raise OHLCVValidationError(f"High ({h}) is lower than Low ({l})")
    if h < o or h < c:
        raise OHLCVValidationError(f"High ({h}) is lower than Open ({o}) or Close ({c})")
    if l > o or l > c:
        raise OHLCVValidationError(f"Low ({l}) is higher than Open ({o}) or Close ({c})")
    if v < 0:
        raise OHLCVValidationError(f"Volume cannot be negative: {v}")
    if number_of_trades < 0:
        raise OHLCVValidationError(f"Number of trades cannot be negative: {number_of_trades}")

    return OHLCVBar(
        symbol=symbol.upper(),
        market_scope=market_scope,
        interval=interval,
        open_time=open_time,
        open=o,
        high=h,
        low=l,
        close=c,
        volume=v,
        close_time=close_time,
        quote_asset_volume=qav,
        number_of_trades=number_of_trades,
        taker_buy_base_volume=tbbv,
        taker_buy_quote_volume=tbqv,
        source=source,
        is_closed=False,  # default, will be overridden later
        raw=row,
    )


def parse_kline_payload(
    payload: list[list[Any]],
    symbol: str,
    market_scope: MarketScope,
    interval: str,
    source: OHLCVSource,
) -> list[OHLCVBar]:
    bars = []
    for row in payload:
        bar = parse_kline_row(row, symbol, market_scope, interval, source)
        bars.append(bar)
    return bars


def bar_to_dict(bar: OHLCVBar) -> dict[str, Any]:
    return {
        "symbol": bar.symbol,
        "market_scope": bar.market_scope.value,
        "interval": bar.interval,
        "open_time": bar.open_time,
        "open": float(bar.open),
        "high": float(bar.high),
        "low": float(bar.low),
        "close": float(bar.close),
        "volume": float(bar.volume),
        "close_time": bar.close_time,
        "quote_asset_volume": float(bar.quote_asset_volume),
        "number_of_trades": bar.number_of_trades,
        "taker_buy_base_volume": float(bar.taker_buy_base_volume),
        "taker_buy_quote_volume": float(bar.taker_buy_quote_volume),
        "source": bar.source.value,
        "is_closed": bar.is_closed,
    }


def bars_to_dataframe(bars: list[OHLCVBar]) -> pd.DataFrame:
    if not bars:
        return pd.DataFrame(columns=EXPECTED_COLUMNS)
    dicts = [bar_to_dict(bar) for bar in bars]
    df = pd.DataFrame(dicts)
    return df[EXPECTED_COLUMNS]


def dataframe_to_bars(df: pd.DataFrame) -> list[OHLCVBar]:
    bars = []
    for _, row in df.iterrows():
        bar = OHLCVBar(
            symbol=row["symbol"],
            market_scope=MarketScope(row["market_scope"]),
            interval=row["interval"],
            open_time=int(row["open_time"]),
            open=Decimal(str(row["open"])),
            high=Decimal(str(row["high"])),
            low=Decimal(str(row["low"])),
            close=Decimal(str(row["close"])),
            volume=Decimal(str(row["volume"])),
            close_time=int(row["close_time"]),
            quote_asset_volume=Decimal(str(row["quote_asset_volume"])),
            number_of_trades=int(row["number_of_trades"]),
            taker_buy_base_volume=Decimal(str(row["taker_buy_base_volume"])),
            taker_buy_quote_volume=Decimal(str(row["taker_buy_quote_volume"])),
            source=OHLCVSource(row["source"]),
            is_closed=bool(row["is_closed"]),
        )
        bars.append(bar)
    return bars


def normalize_ohlcv_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

    missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise OHLCVParseError(f"Missing required columns in dataframe: {missing_cols}")

    return df[EXPECTED_COLUMNS].copy()
