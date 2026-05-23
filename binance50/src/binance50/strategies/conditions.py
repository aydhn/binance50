import math
from enum import StrEnum
from typing import Any

import pandas as pd

from binance50.strategies.models import StrategyConditionEvidence


class ConditionOperator(StrEnum):
    gt = "gt"
    gte = "gte"
    lt = "lt"
    lte = "lte"
    eq = "eq"
    neq = "neq"
    between = "between"
    crosses_above = "crosses_above"
    crosses_below = "crosses_below"
    is_positive = "is_positive"
    is_negative = "is_negative"
    is_not_nan = "is_not_nan"


def safe_numeric(value: Any) -> float | None:
    if pd.isna(value) or value is None:
        return None
    try:
        fval = float(value)
        if math.isinf(fval) or math.isnan(fval):
            return None
        return fval
    except (ValueError, TypeError):
        return None


def is_valid_feature_value(value: Any) -> bool:
    return safe_numeric(value) is not None


def evaluate_condition(
    value: float | None,
    operator: ConditionOperator | str,
    threshold: float | None = None,
    upper: float | None = None,
    previous_value: float | None = None,
) -> bool:

    if value is None or pd.isna(value):
        return False

    val = float(value)

    if math.isnan(val) or math.isinf(val):
        return False

    op = ConditionOperator(operator)

    if op == ConditionOperator.is_not_nan:
        return True

    if op == ConditionOperator.is_positive:
        return val > 0
    if op == ConditionOperator.is_negative:
        return val < 0

    if threshold is None:
        return False

    if op == ConditionOperator.gt:
        return val > threshold
    if op == ConditionOperator.gte:
        return val >= threshold
    if op == ConditionOperator.lt:
        return val < threshold
    if op == ConditionOperator.lte:
        return val <= threshold
    if op == ConditionOperator.eq:
        return math.isclose(val, threshold, rel_tol=1e-9)
    if op == ConditionOperator.neq:
        return not math.isclose(val, threshold, rel_tol=1e-9)

    if op == ConditionOperator.between:
        if upper is None:
            return False
        return threshold <= val <= upper

    if op == ConditionOperator.crosses_above:
        if previous_value is None or pd.isna(previous_value):
            return False
        return previous_value <= threshold and val > threshold

    if op == ConditionOperator.crosses_below:
        if previous_value is None or pd.isna(previous_value):
            return False
        return previous_value >= threshold and val < threshold

    return False


def crosses_above(series: pd.Series, threshold: float) -> pd.Series:
    shifted = series.shift(1)
    return (shifted <= threshold) & (series > threshold)


def crosses_below(series: pd.Series, threshold: float) -> pd.Series:
    shifted = series.shift(1)
    return (shifted >= threshold) & (series < threshold)


def build_condition_evidence(
    feature_name: str,
    operator: str,
    threshold: float | str | None,
    actual_value: float | str | None,
    passed: bool,
    weight: float = 1.0,
    message: str | None = None,
) -> StrategyConditionEvidence:
    return StrategyConditionEvidence(
        feature_name=feature_name,
        operator=operator,
        threshold=threshold,
        actual_value=actual_value,
        passed=passed,
        weight=weight,
        message=message,
    )
