from binance50.config.models import AppConfig

# Extends basic logic from connectors.stream_names
from binance50.connectors.stream_names import (
    build_agg_trade_stream,
    build_book_ticker_stream,
    build_depth_stream,
    build_kline_stream,
    build_mini_ticker_stream,
    build_trade_stream,
    normalize_symbol_for_stream,
    validate_stream_name,
)
from binance50.core.enums import MarketScope
from binance50.streams.event_types import StreamType


def build_stream_name(
    symbol: str,
    stream_type: StreamType,
    interval: str | None = None,
    depth_levels: int | None = None,
    speed_ms: int | None = None,
    market_scope: MarketScope = MarketScope.SPOT,
) -> str:
    sym = normalize_symbol_for_stream(symbol)

    if stream_type == StreamType.kline:
        if not interval:
            raise ValueError("Interval is required for kline stream")
        return build_kline_stream(sym, interval)
    elif stream_type == StreamType.book_ticker:
        return build_book_ticker_stream(sym)
    elif stream_type == StreamType.mini_ticker:
        return build_mini_ticker_stream(sym)
    elif stream_type == StreamType.ticker:
        return f"{sym}@ticker"
    elif stream_type == StreamType.trade:
        return build_trade_stream(sym)
    elif stream_type == StreamType.agg_trade:
        return build_agg_trade_stream(sym)
    elif stream_type in (StreamType.partial_depth, StreamType.diff_depth):
        if stream_type == StreamType.partial_depth and depth_levels:
            name = f"{sym}@depth{depth_levels}"
            if speed_ms:
                name += f"@{speed_ms}ms"
            return name
        return build_depth_stream(sym, speed_ms)
    elif stream_type == StreamType.mark_price:
        if market_scope != MarketScope.USDM_FUTURES:
            raise ValueError("markPrice stream is only valid for USDM_FUTURES")
        return build_mark_price_stream_name(sym)
    else:
        raise ValueError(f"Unsupported stream type builder for {stream_type.value}")


def build_ticker_stream_name(symbol: str) -> str:
    sym = normalize_symbol_for_stream(symbol)
    return f"{sym}@ticker"


def build_mark_price_stream_name(symbol: str) -> str:
    sym = normalize_symbol_for_stream(symbol)
    return f"{sym}@markPrice"


def parse_stream_name(stream_name: str) -> dict:
    parts = stream_name.split("@")
    if len(parts) < 2:
        return {"symbol": "unknown", "type": "unknown"}

    symbol = parts[0].upper()
    stream_suffix = parts[1]

    interval = None
    if stream_suffix.startswith("kline_"):
        stream_type = StreamType.kline
        interval = stream_suffix.split("_")[1]
    elif stream_suffix == "trade":
        stream_type = StreamType.trade
    elif stream_suffix == "aggTrade":
        stream_type = StreamType.agg_trade
    elif stream_suffix == "miniTicker":
        stream_type = StreamType.mini_ticker
    elif stream_suffix == "ticker":
        stream_type = StreamType.ticker
    elif stream_suffix == "bookTicker":
        stream_type = StreamType.book_ticker
    elif stream_suffix.startswith("depth"):
        stream_type = (
            StreamType.partial_depth
            if any(x.isdigit() for x in stream_suffix)
            else StreamType.diff_depth
        )
    elif stream_suffix == "markPrice":
        stream_type = StreamType.mark_price
    else:
        stream_type = StreamType.unknown

    return {
        "symbol": symbol,
        "type": stream_type,
        "interval": interval,
    }


def normalize_stream_symbol(symbol: str) -> str:
    return normalize_symbol_for_stream(symbol).lower()


def validate_stream_name_with_config(stream_name: str, config: AppConfig) -> None:
    validate_stream_name(stream_name)
    parsed = parse_stream_name(stream_name)
    st = parsed["type"].value if isinstance(parsed["type"], StreamType) else str(parsed["type"])
    if st != "unknown" and st not in config.streams.allowed_stream_types:
        raise ValueError(f"Stream type {st} is not allowed by config")
