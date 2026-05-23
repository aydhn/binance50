import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from binance50.config.models import AppConfig
from binance50.strategies.conditions import (
    ConditionOperator,
    build_condition_evidence,
    evaluate_condition,
)
from binance50.strategies.models import (
    StrategyCandidateStrength,
    StrategyConditionEvidence,
    StrategyDirection,
)


class RuleCondition(BaseModel):
    model_config = ConfigDict(frozen=True)

    feature: str
    operator: ConditionOperator
    threshold: float | None = None
    upper: float | None = None
    weight: float = 1.0
    required: bool = True


class RuleBlock(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    conditions: list[RuleCondition] = Field(default_factory=list)
    min_required_passed: int | None = None
    all_required_must_pass: bool = True
    direction_if_passed: StrategyDirection
    strength_if_passed: StrategyCandidateStrength
    base_confidence: float = 50.0


class RuleEvaluationResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    rule_name: str
    passed: bool
    evidence: list[StrategyConditionEvidence] = Field(default_factory=list)
    confidence_contribution: float = 0.0
    direction: StrategyDirection | None = None
    strength: StrategyCandidateStrength | None = None
    warnings: list[str] = Field(default_factory=list)


def evaluate_rule_block(
    row: pd.Series, previous_row: pd.Series | None, block: RuleBlock
) -> RuleEvaluationResult:
    evidence_list = []
    passed_required = 0
    passed_total = 0
    failed_required = 0
    total_required = 0
    warnings = []

    for cond in block.conditions:
        val = row.get(cond.feature, None)
        prev_val = previous_row.get(cond.feature, None) if previous_row is not None else None

        is_passed = evaluate_condition(
            value=val,
            operator=cond.operator,
            threshold=cond.threshold,
            upper=cond.upper,
            previous_value=prev_val,
        )

        evidence = build_condition_evidence(
            feature_name=cond.feature,
            operator=cond.operator,
            threshold=cond.threshold,
            actual_value=val,
            passed=is_passed,
            weight=cond.weight,
        )
        evidence_list.append(evidence)

        if cond.required:
            total_required += 1
            if is_passed:
                passed_required += 1
            else:
                failed_required += 1

        if is_passed:
            passed_total += 1

    overall_pass = True
    if block.all_required_must_pass and failed_required > 0:
        overall_pass = False

    if block.min_required_passed is not None and passed_total < block.min_required_passed:
        overall_pass = False

    conf = block.base_confidence if overall_pass else 0.0
    # Additional confidence rules could be factored by weights of passed non-required conditions

    return RuleEvaluationResult(
        rule_name=block.name,
        passed=overall_pass,
        evidence=evidence_list,
        confidence_contribution=max(0.0, min(100.0, conf)),
        direction=block.direction_if_passed if overall_pass else None,
        strength=block.strength_if_passed if overall_pass else None,
        warnings=warnings,
    )


def combine_rule_results(
    results: list[RuleEvaluationResult],
) -> tuple[StrategyDirection, StrategyCandidateStrength, float]:
    passed_results = [r for r in results if r.passed and r.direction]
    if not passed_results:
        return StrategyDirection.no_action, StrategyCandidateStrength.weak, 0.0

    directions = set([r.direction for r in passed_results])
    if len(directions) > 1:
        # Conflict
        return StrategyDirection.no_action, StrategyCandidateStrength.weak, 0.0

    direction = list(directions)[0]

    # Simplistic combination logic for strength and confidence
    max_strength = StrategyCandidateStrength.weak
    total_conf = 0.0
    for r in passed_results:
        if r.strength == StrategyCandidateStrength.strong:
            max_strength = StrategyCandidateStrength.strong
        elif (
            r.strength == StrategyCandidateStrength.medium
            and max_strength != StrategyCandidateStrength.strong
        ):
            max_strength = StrategyCandidateStrength.medium

        total_conf += r.confidence_contribution

    final_conf = max(0.0, min(100.0, total_conf))

    return direction, max_strength, final_conf


def validate_rule_block(block: RuleBlock, config: AppConfig) -> None:
    if len(block.conditions) > config.strategies.max_conditions_per_plugin:
        raise ValueError(
            f"RuleBlock {block.name} exceeds max conditions limit ({config.strategies.max_conditions_per_plugin})"
        )
