import pytest
from decimal import Decimal
from binance50.app import load_config as get_config
from binance50.core.exceptions import BinanceFilterValidationError
from binance50.execution.filters import (
    load_symbol_filters_from_fixture,
    validate_price_filter,
    validate_lot_size,
    validate_min_notional,
    build_filter_validation_report
)

def test_load_fixture():
    config = get_config()
    snapshot = load_symbol_filters_from_fixture("BTCUSDT", config)
    assert snapshot.symbol == "BTCUSDT"
    assert snapshot.price_filter["tickSize"] == Decimal("0.01")

def test_validate_filters():
    config = get_config()
    snapshot = load_symbol_filters_from_fixture("BTCUSDT", config)
    assert validate_price_filter(Decimal("10.01"), snapshot, config)
    assert not validate_price_filter(Decimal("10.001"), snapshot, config)

    assert validate_lot_size(Decimal("0.005"), snapshot, config)
    assert not validate_lot_size(Decimal("0.0055"), snapshot, config)

    assert validate_min_notional(Decimal("1000"), Decimal("0.05"), snapshot, config)
    assert not validate_min_notional(Decimal("100"), Decimal("0.05"), snapshot, config)

def test_network_fetch_forbidden_raises_if_config_changed():
    config = get_config()
    config.execution.binance_filters.network_fetch_forbidden = False
    with pytest.raises(BinanceFilterValidationError):
        load_symbol_filters_from_fixture("BTCUSDT", config)
