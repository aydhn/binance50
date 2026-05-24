from binance50.config.models import AppConfig
from binance50.regimes.models import (
    MarketRegime,
    RegimeClassification,
    RegimeFamily,
    RegimeMethod,
    RegimeRiskContext,
)
from binance50.regimes.transitions import detect_regime_transitions


def test_transition_detection():
    config = AppConfig()

    c1 = RegimeClassification(
        regime_id="1",
        symbol="BTC",
        market_scope="spot",
        interval="1m",
        open_time=1,
        close_time=2,
        regime=MarketRegime.trend_up,
        family=RegimeFamily.trend,
        method=RegimeMethod.rule_based,
        confidence=50,
        risk_context=RegimeRiskContext.unknown,
        explanation={},
        feature_snapshot={},
        created_at_utc=0,
    )
    c2 = RegimeClassification(
        regime_id="2",
        symbol="BTC",
        market_scope="spot",
        interval="1m",
        open_time=2,
        close_time=3,
        regime=MarketRegime.range_bound,
        family=RegimeFamily.range,
        method=RegimeMethod.rule_based,
        confidence=50,
        risk_context=RegimeRiskContext.unknown,
        explanation={},
        feature_snapshot={},
        created_at_utc=0,
    )

    t = detect_regime_transitions([c1, c2], config)
    assert len(t) == 1
    assert t[0].from_regime == MarketRegime.trend_up
    assert t[0].to_regime == MarketRegime.range_bound
