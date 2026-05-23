import pandas as pd

from binance50.strategies.conditions import ConditionOperator
from binance50.strategies.rule_dsl import RuleBlock, RuleCondition, evaluate_rule_block


def test_rule_dsl():
    block = RuleBlock(
        name="test_rule",
        conditions=[RuleCondition(feature="close", operator=ConditionOperator.gt, threshold=100)],
        direction_if_passed="bullish",
        strength_if_passed="medium",
    )

    row = pd.Series({"close": 150})
    res = evaluate_rule_block(row, None, block)
    assert res.passed
    assert res.direction == "bullish"

    row2 = pd.Series({"close": 50})
    res2 = evaluate_rule_block(row2, None, block)
    assert not res2.passed
    assert res2.direction is None
