from binance50.strategies.conditions import ConditionOperator, evaluate_condition


def test_evaluate_condition():
    assert evaluate_condition(10.5, ConditionOperator.gt, 10.0)
    assert not evaluate_condition(10.0, ConditionOperator.gt, 10.0)

    assert evaluate_condition(10.0, ConditionOperator.eq, 10.0)
    assert evaluate_condition(10.0, ConditionOperator.gte, 10.0)

    assert evaluate_condition(15, ConditionOperator.between, 10, 20)
    assert not evaluate_condition(5, ConditionOperator.between, 10, 20)

    assert evaluate_condition(10.5, ConditionOperator.crosses_above, 10.0, None, 9.5)
    assert not evaluate_condition(9.5, ConditionOperator.crosses_above, 10.0, None, 10.5)

    assert evaluate_condition(10, ConditionOperator.is_positive)
    assert evaluate_condition(-10, ConditionOperator.is_negative)
