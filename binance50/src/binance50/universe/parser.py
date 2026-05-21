from decimal import Decimal, InvalidOperation
from typing import Any

from binance50.core.enums import MarketScope
from binance50.universe.models import (
    BookTicker,
    SymbolFilter,
    SymbolFilterType,
    SymbolMetadata,
    SymbolStatus,
    Ticker24h,
)


def safe_decimal(value: Any, default: Decimal | None = None) -> Decimal | None:
    if value is None:
        return default
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return default


def normalize_symbol_status(status: str | None) -> SymbolStatus:
    if not status:
        return SymbolStatus.UNKNOWN
    status = status.upper()
    if status == "TRADING":
        return SymbolStatus.TRADING
    if status == "HALT":
        return SymbolStatus.HALT
    if status == "BREAK":
        return SymbolStatus.BREAK_STATUS
    return SymbolStatus.UNKNOWN


def parse_permissions(raw: Any) -> list[str]:
    if isinstance(raw, list):
        return [str(x) for x in raw]
    return []


def parse_symbol_filters(filters: list[dict[str, Any]]) -> dict[SymbolFilterType, SymbolFilter]:
    parsed: dict[SymbolFilterType, SymbolFilter] = {}
    for f in filters:
        ftype_str = f.get("filterType", "").upper()
        try:
            ftype = SymbolFilterType(ftype_str.lower())
        except ValueError:
            ftype = SymbolFilterType.UNKNOWN

        parsed[ftype] = SymbolFilter(
            filter_type=ftype,
            raw=f,
            min_price=safe_decimal(f.get("minPrice")),
            max_price=safe_decimal(f.get("maxPrice")),
            tick_size=safe_decimal(f.get("tickSize")),
            min_qty=safe_decimal(f.get("minQty")),
            max_qty=safe_decimal(f.get("maxQty")),
            step_size=safe_decimal(f.get("stepSize")),
            min_notional=safe_decimal(f.get("minNotional") or f.get("notional")),
            max_notional=safe_decimal(f.get("maxNotional")),
            apply_to_market=f.get("applyToMarket"),
            avg_price_mins=f.get("avgPriceMins"),
        )
    return parsed


def parse_spot_exchange_info(payload: dict[str, Any]) -> list[SymbolMetadata]:
    symbols = payload.get("symbols", [])
    result: list[SymbolMetadata] = []
    for s in symbols:
        symbol = s.get("symbol", "").upper()
        if not symbol:
            continue
        result.append(
            SymbolMetadata(
                symbol=symbol,
                base_asset=s.get("baseAsset", "").upper(),
                quote_asset=s.get("quoteAsset", "").upper(),
                status=normalize_symbol_status(s.get("status")),
                market_scope=MarketScope.SPOT,
                permissions=parse_permissions(s.get("permissions", [])),
                filters=parse_symbol_filters(s.get("filters", [])),
                raw=s,
            )
        )
    return result


def parse_usdm_exchange_info(payload: dict[str, Any]) -> list[SymbolMetadata]:
    symbols = payload.get("symbols", [])
    result: list[SymbolMetadata] = []
    for s in symbols:
        symbol = s.get("symbol", "").upper()
        if not symbol:
            continue
        result.append(
            SymbolMetadata(
                symbol=symbol,
                base_asset=s.get("baseAsset", "").upper(),
                quote_asset=s.get("quoteAsset", "").upper(),
                status=normalize_symbol_status(s.get("status")),
                market_scope=MarketScope.USDM_FUTURES,
                contract_type=s.get("contractType"),
                margin_asset=s.get("marginAsset", "").upper(),
                filters=parse_symbol_filters(s.get("filters", [])),
                raw=s,
            )
        )
    return result


def parse_24h_tickers(
    payload: list[dict[str, Any]] | dict[str, Any], market_scope: MarketScope
) -> dict[str, Ticker24h]:
    if isinstance(payload, dict):
        if "symbol" in payload:
            payload = [payload]
        else:
            return {}

    result: dict[str, Ticker24h] = {}
    for t in payload:
        symbol = t.get("symbol", "").upper()
        if not symbol:
            continue
        import contextlib

        with contextlib.suppress(ValueError, TypeError):
            result[symbol] = Ticker24h(
                symbol=symbol,
                price_change_percent=safe_decimal(t.get("priceChangePercent"), Decimal(0)),
                last_price=safe_decimal(t.get("lastPrice"), Decimal(0)),
                volume=safe_decimal(t.get("volume"), Decimal(0)),
                quote_volume=safe_decimal(t.get("quoteVolume"), Decimal(0)),
                trade_count=int(t.get("count", 0)),
                raw=t,
            )
    return result


def parse_book_tickers(
    payload: list[dict[str, Any]] | dict[str, Any], market_scope: MarketScope
) -> dict[str, BookTicker]:
    if isinstance(payload, dict):
        if "symbol" in payload:
            payload = [payload]
        else:
            return {}

    result: dict[str, BookTicker] = {}
    for t in payload:
        symbol = t.get("symbol", "").upper()
        if not symbol:
            continue
        import contextlib

        with contextlib.suppress(ValueError, TypeError):
            result[symbol] = BookTicker(
                symbol=symbol,
                bid_price=safe_decimal(t.get("bidPrice"), Decimal(0)),
                bid_qty=safe_decimal(t.get("bidQty"), Decimal(0)),
                ask_price=safe_decimal(t.get("askPrice"), Decimal(0)),
                ask_qty=safe_decimal(t.get("askQty"), Decimal(0)),
                raw=t,
            )
    return result
