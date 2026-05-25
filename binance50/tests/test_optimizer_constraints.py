import pytest

from binance50.config.models import AppConfig
from binance50.optimizer.constraints import (
    compute_parameter_complexity,
    validate_cross_parameter_constraints,
    validate_parameter_set,
)
from binance50.optimizer.models import ParameterSet


def test_rsi_oversold_overbought():
    pset = ParameterSet(
        parameter_set_id="1",
        values={
            "strategy.mean_reversion.rsi_oversold": 70,
            "strategy.mean_reversion.rsi_overbought": 30,
        },
        config_patch={},
        hash="",
    )
    errors = validate_cross_parameter_constraints(pset)
    assert any("rsi_oversold must be < rsi_overbought" in e for e in errors)


def test_risk_thresholds_ordered():
    pset = ParameterSet(
        parameter_set_id="1",
        values={
            "signals.thresholds.research_candidate_min": 70,
            "signals.thresholds.risk_review_min": 60,
        },
        config_patch={},
        hash="",
    )
    errors = validate_cross_parameter_constraints(pset)
    assert any("research_candidate_min must be <= risk_review_min" in e for e in errors)


def test_live_params_rejected():
    pset = ParameterSet(
        parameter_set_id="1", values={"live.trading.enabled": True}, config_patch={}, hash=""
    )
    config = AppConfig()
    with pytest.raises(ValueError, match="forbidden"):
        validate_parameter_set(pset, config)


def test_execution_params_rejected():
    pset = ParameterSet(
        parameter_set_id="1", values={"execution.order.quantity": 1}, config_patch={}, hash=""
    )
    config = AppConfig()
    with pytest.raises(ValueError, match="forbidden"):
        validate_parameter_set(pset, config)


def test_complexity_score():
    pset = ParameterSet(parameter_set_id="1", values={"a": 1, "b": 2}, config_patch={}, hash="")
    assert compute_parameter_complexity(pset) == 2.0
