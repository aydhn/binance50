from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional

from binance50.config.models import AppConfig
from binance50.core.exceptions import BinanceFilterValidationError


@dataclass
class BinanceSymbolFilterSnapshot:
    symbol: str
    price_filter: dict[str, Decimal]
    lot_size: dict[str, Decimal]
    min_notional: dict[str, Decimal]
    notional: dict[str, Decimal]
    market_lot_size: dict[str, Decimal]
    percent_price: dict[str, Decimal]
    raw_filters: list[dict[str, Any]]
    source: str
    source_hash: str
    loaded_at_utc: datetime
    metadata: dict[str, Any]


@dataclass
class BinanceFilterValidationReport:
    symbol: str
    price_filter_passed: bool
    lot_size_passed: bool
    min_notional_passed: bool
    notional_passed: bool
    market_lot_size_passed: bool
    percent_price_checked: bool
    missing_filters: list[str]
    validation_passed: bool
    warnings: list[str]
    metadata: dict[str, Any]


def load_symbol_filters_from_fixture(symbol: str, config: AppConfig) -> BinanceSymbolFilterSnapshot:
    if config.execution.binance_filters.network_fetch_forbidden:
        # Skeleton implementation returning a mock fixture
        return BinanceSymbolFilterSnapshot(
            symbol=symbol,
            price_filter={"tickSize": Decimal("0.01"), "minPrice": Decimal("0.01"), "maxPrice": Decimal("1000000")},
            lot_size={"stepSize": Decimal("0.001"), "minQty": Decimal("0.001"), "maxQty": Decimal("10000")},
            min_notional={"minNotional": Decimal("10.0")},
            notional={"minNotional": Decimal("10.0")},
            market_lot_size={},
            percent_price={},
            raw_filters=[],
            source="fixture_or_cached_exchange_info_only",
            source_hash="mock_hash_123",
            loaded_at_utc=datetime.now(timezone.utc),
            metadata={"skeleton": True}
        )
    raise BinanceFilterValidationError("Network fetch is forbidden, but no valid fixture source was found.")


def load_symbol_filters_from_cache(symbol: str, config: AppConfig) -> BinanceSymbolFilterSnapshot:
    return load_symbol_filters_from_fixture(symbol, config)


def validate_price_filter(price: Optional[Decimal], snapshot: BinanceSymbolFilterSnapshot, config: AppConfig) -> bool:
    if not config.execution.binance_filters.validate_price_filter or price is None:
        return True
    tick = snapshot.price_filter.get("tickSize")
    if tick and (price % tick) != 0:
        return False
    return True


def validate_lot_size(quantity: Optional[Decimal], snapshot: BinanceSymbolFilterSnapshot, config: AppConfig) -> bool:
    if not config.execution.binance_filters.validate_lot_size or quantity is None:
        return True
    step = snapshot.lot_size.get("stepSize")
    if step and (quantity % step) != 0:
        return False
    return True


def validate_min_notional(price: Optional[Decimal], quantity: Optional[Decimal], snapshot: BinanceSymbolFilterSnapshot, config: AppConfig) -> bool:
    if not config.execution.binance_filters.validate_min_notional or price is None or quantity is None:
        return True
    notional_val = price * quantity
    min_n = snapshot.min_notional.get("minNotional")
    if min_n and notional_val < min_n:
        return False
    return True


def validate_notional(price: Optional[Decimal], quantity: Optional[Decimal], snapshot: BinanceSymbolFilterSnapshot, config: AppConfig) -> bool:
    if not config.execution.binance_filters.validate_notional or price is None or quantity is None:
        return True
    notional_val = price * quantity
    min_n = snapshot.notional.get("minNotional")
    if min_n and notional_val < min_n:
        return False
    return True


def build_filter_validation_report(intent: Any, snapshot: BinanceSymbolFilterSnapshot, config: AppConfig) -> BinanceFilterValidationReport:
    # intent: ExecutionIntentDraft
    missing = []
    if not snapshot.price_filter: missing.append("PRICE_FILTER")
    if not snapshot.lot_size: missing.append("LOT_SIZE")
    if not snapshot.notional and not snapshot.min_notional: missing.append("NOTIONAL")

    if config.execution.binance_filters.reject_missing_filters and missing:
        raise BinanceFilterValidationError(f"Missing essential filters: {missing}")

    p_pass = validate_price_filter(intent.price, snapshot, config)
    l_pass = validate_lot_size(intent.quantity, snapshot, config)
    mn_pass = validate_min_notional(intent.price, intent.quantity, snapshot, config)
    n_pass = validate_notional(intent.price, intent.quantity, snapshot, config)

    passed = p_pass and l_pass and mn_pass and n_pass

    # In Phase 28, quantity and price are expected to be None, so these checks default to True.
    warnings = []
    if getattr(intent, 'price', None) is None or getattr(intent, 'quantity', None) is None:
        warnings.append("not_applicable_sandbox")

    return BinanceFilterValidationReport(
        symbol=snapshot.symbol,
        price_filter_passed=p_pass,
        lot_size_passed=l_pass,
        min_notional_passed=mn_pass,
        notional_passed=n_pass,
        market_lot_size_passed=True,
        percent_price_checked=False,
        missing_filters=missing,
        validation_passed=passed,
        warnings=warnings,
        metadata={"source": snapshot.source, "hash": snapshot.source_hash}
    )
