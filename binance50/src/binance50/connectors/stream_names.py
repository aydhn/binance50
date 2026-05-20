import re
from typing import Literal

VALID_INTERVALS = {
    "1m",
    "3m",
    "5m",
    "15m",
    "30m",
    "1h",
    "2h",
    "4h",
    "6h",
    "8h",
    "12h",
    "1d",
    "3d",
    "1w",
    "1M",
}


def normalize_symbol_for_stream(symbol: str) -> str:
    if not symbol:
        raise ValueError("Symbol cannot be empty")
    if not re.match(r"^[a-zA-Z0-9]+$", symbol):
        raise ValueError(f"Invalid symbol format: {symbol}")
    return symbol.lower()


def validate_stream_name(stream: str) -> None:
    if not stream:
        raise ValueError("Stream name cannot be empty")


def build_kline_stream(symbol: str, interval: str) -> str:
    if interval not in VALID_INTERVALS:
        raise ValueError(f"Invalid interval: {interval}")
    sym = normalize_symbol_for_stream(symbol)
    return f"{sym}@kline_{interval}"


def build_trade_stream(symbol: str) -> str:
    sym = normalize_symbol_for_stream(symbol)
    return f"{sym}@trade"


def build_agg_trade_stream(symbol: str) -> str:
    sym = normalize_symbol_for_stream(symbol)
    return f"{sym}@aggTrade"


def build_mini_ticker_stream(symbol: str) -> str:
    sym = normalize_symbol_for_stream(symbol)
    return f"{sym}@miniTicker"


def build_book_ticker_stream(symbol: str) -> str:
    sym = normalize_symbol_for_stream(symbol)
    return f"{sym}@bookTicker"


def build_depth_stream(symbol: str, speed_ms: int | None = None) -> str:
    if speed_ms not in (None, 100, 1000):
        raise ValueError("Depth speed must be 100 or 1000")
    sym = normalize_symbol_for_stream(symbol)
    if speed_ms:
        return f"{sym}@depth@{speed_ms}ms"
    return f"{sym}@depth"


def build_combined_stream_path(streams: list[str]) -> str:
    if not streams:
        raise ValueError("Streams list cannot be empty")
    return "/stream?streams=" + "/".join(streams)


def build_raw_stream_path(stream: str) -> str:
    validate_stream_name(stream)
    return f"/ws/{stream}"


def classify_usdm_stream_route(stream: str) -> Literal["public", "market", "private"]:
    # Mock classification for now based on stream name heuristics
    if "kline" in stream or "depth" in stream or "trade" in stream or "ticker" in stream:
        return "market"
    # Fallback to public
    return "public"
