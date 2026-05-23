from enum import StrEnum


class StreamType(StrEnum):
    kline = "kline"
    mini_ticker = "miniTicker"
    ticker = "ticker"
    book_ticker = "bookTicker"
    partial_depth = "partialDepth"
    diff_depth = "diffDepth"
    trade = "trade"
    agg_trade = "aggTrade"
    mark_price = "markPrice"
    force_order = "forceOrder"
    unknown = "unknown"


class StreamEventStatus(StrEnum):
    valid = "valid"
    warning = "warning"
    invalid = "invalid"
    stale = "stale"
    duplicate = "duplicate"
    out_of_order = "out_of_order"


class StreamSource(StrEnum):
    fixture = "fixture"
    replay = "replay"
    mock = "mock"
    binance_spot_ws = "binance_spot_ws"
    binance_usdm_ws = "binance_usdm_ws"


class StreamRoute(StrEnum):
    spot_raw = "spot_raw"
    spot_combined = "spot_combined"
    usdm_market = "usdm_market"
    usdm_public = "usdm_public"
    usdm_private = "usdm_private"
    unknown = "unknown"
