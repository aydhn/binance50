import pytest

from binance50.config.models import AppConfig
from binance50.safety.universe_guard import (
    UniverseSafetyError,
    assert_universe_config_safe,
    assert_universe_result_safe,
    build_universe_safety_report,
)
from binance50.universe.models import (
    SymbolDecisionStatus,
    SymbolMetadata,
    SymbolRejectionReason,
    UniverseCandidate,
    UniverseSelectionResult,
)


def test_default_config_safe():
    c = AppConfig()
    # should not raise
    assert_universe_config_safe(c)


def test_config_unsafe_max_symbols():
    c = AppConfig()
    c.universe.max_symbols_initial = 100
    with pytest.raises(UniverseSafetyError, match="unsafely high"):
        assert_universe_config_safe(c)


def test_config_unsafe_allow_stablecoin():
    c = AppConfig()
    c.universe.allow_stablecoin_pairs = True
    with pytest.raises(UniverseSafetyError, match="allow_stablecoin_pairs is unsafely set to True"):
        assert_universe_config_safe(c)


def test_result_safe():
    c = AppConfig()
    m = SymbolMetadata(
        symbol="BTCUSDT",
        base_asset="BTC",
        quote_asset="USDT",
        status="trading",
        market_scope="spot",
    )
    candidate = UniverseCandidate(
        symbol="BTCUSDT",
        market_scope="spot",
        metadata=m,
        decision_status=SymbolDecisionStatus.ACCEPTED,
    )
    result = UniverseSelectionResult(
        selected_symbols=["BTCUSDT"], candidates={"BTCUSDT": candidate}
    )

    # should not raise
    assert_universe_result_safe(result, c)


def test_result_unsafe_blacklisted():
    c = AppConfig()
    m = SymbolMetadata(
        symbol="BADUSDT",
        base_asset="BAD",
        quote_asset="USDT",
        status="trading",
        market_scope="spot",
    )
    candidate = UniverseCandidate(
        symbol="BADUSDT",
        market_scope="spot",
        metadata=m,
        decision_status=SymbolDecisionStatus.ACCEPTED,
        rejection_reasons=[SymbolRejectionReason.BLACKLISTED],
    )
    result = UniverseSelectionResult(
        selected_symbols=["BADUSDT"], candidates={"BADUSDT": candidate}
    )

    with pytest.raises(UniverseSafetyError, match="Blacklisted symbol selected"):
        assert_universe_result_safe(result, c)


def test_safety_report():
    c = AppConfig()
    report = build_universe_safety_report(c)
    assert report["config_status"] == "safe"
    assert report["result_status"] == "not_evaluated"
    assert report["overall_status"] == "safe"
