from binance50.regimes.models import (
    MarketRegime,
    RegimeClassification,
    RegimeFamily,
    RegimeMethod,
    RegimeRiskContext,
)


def test_regime_classification_valid():
    c = RegimeClassification(
        regime_id="BTC_100",
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        open_time=100,
        close_time=159,
        regime=MarketRegime.trend_up,
        family=RegimeFamily.trend,
        method=RegimeMethod.rule_based,
        confidence=80.0,
        risk_context=RegimeRiskContext.risk_on_candidate,
        explanation={"reasons": ["test"]},
        feature_snapshot={"adx": 30.0},
        created_at_utc=0,
    )
    assert c.confidence == 80.0
    assert c.regime == MarketRegime.trend_up


def test_no_execution_fields():
    # If order_id was added, Pydantic would allow if extra=allow or explicitly defined.
    # Our schema does not define order_id. We assert it's not present.
    c = RegimeClassification(
        regime_id="BTC_100",
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        open_time=100,
        close_time=159,
        regime=MarketRegime.trend_up,
        family=RegimeFamily.trend,
        method=RegimeMethod.rule_based,
        confidence=80.0,
        risk_context=RegimeRiskContext.risk_on_candidate,
        explanation={"reasons": ["test"]},
        feature_snapshot={"adx": 30.0},
        created_at_utc=0,
    )
    d = c.model_dump()
    assert "order_id" not in d
    assert "quantity" not in d
