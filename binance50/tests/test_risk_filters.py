import pytest

from binance50.config.models import AppConfig
from binance50.risk.filters import (
    build_symbol_filter_risk_report,
    check_lot_size_metadata,
    check_min_notional_metadata,
    check_price_filter_metadata,
    extract_risk_relevant_filters,
)


@pytest.fixture
def test_config():
    return AppConfig()


def test_extract_risk_relevant_filters():
    meta = {
        "filters": [
            {"filterType": "PRICE_FILTER", "minPrice": "1.0"},
            {"filterType": "MAX_NUM_ORDERS"},
            {"filterType": "LOT_SIZE", "minQty": "0.1"},
        ]
    }
    extracted = extract_risk_relevant_filters(meta)
    assert "PRICE_FILTER" in extracted
    assert "LOT_SIZE" in extracted
    assert "MAX_NUM_ORDERS" not in extracted


def test_check_metadata_presence(test_config):
    test_config.risk.spot.require_price_filter_check = True
    test_config.risk.spot.require_lot_size_check = True
    test_config.risk.spot.require_min_notional_check = True

    assert check_price_filter_metadata(None, test_config).passed is False
    assert check_lot_size_metadata(None, test_config).passed is False
    assert check_min_notional_metadata(None, test_config).passed is False

    meta = {"filters": []}
    assert check_price_filter_metadata(meta, test_config).passed is True


def test_build_symbol_filter_risk_report():
    report = build_symbol_filter_risk_report(None)
    assert report["status"] == "missing"
