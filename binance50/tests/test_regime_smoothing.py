from binance50.config.models import AppConfig
from binance50.regimes.models import (
    MarketRegime,
    RegimeClassification,
    RegimeFamily,
    RegimeMethod,
    RegimeRiskContext,
)
from binance50.regimes.smoothing import apply_majority_vote_smoothing


def test_majority_vote():
    config = AppConfig()
    config.regimes.smoothing.majority_vote_window = 3

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
        regime=MarketRegime.trend_up,
        family=RegimeFamily.trend,
        method=RegimeMethod.rule_based,
        confidence=50,
        risk_context=RegimeRiskContext.unknown,
        explanation={},
        feature_snapshot={},
        created_at_utc=0,
    )
    c3 = RegimeClassification(
        regime_id="3",
        symbol="BTC",
        market_scope="spot",
        interval="1m",
        open_time=3,
        close_time=4,
        regime=MarketRegime.trend_down,
        family=RegimeFamily.trend,
        method=RegimeMethod.rule_based,
        confidence=50,
        risk_context=RegimeRiskContext.unknown,
        explanation={},
        feature_snapshot={},
        created_at_utc=0,
    )

    res = apply_majority_vote_smoothing([c1, c2, c3], config)
    assert res[2].regime == MarketRegime.trend_up  # Smoothed based on past 2
