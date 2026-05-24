from typing import Any

from binance50.config.models import AppConfig
from binance50.signals.models import ScoredSignalCandidate
from binance50.strategies.models import SignalCandidate


def assert_no_execution_objects(payload: Any) -> None:
    """Recursively check payload for execution-related fields."""
    if isinstance(payload, dict):
        forbidden_fields = {
            "order_id",
            "quantity",
            "qty",
            "leverage",
            "margin",
            "entry_price",
            "exit_price",
            "stop_loss",
            "take_profit",
            "liquidation",
            "order_type",
            "time_in_force",
            "reduce_only",
            "position_side",
            "side",
        }
        for k, v in payload.items():
            if k.lower() in forbidden_fields:
                from binance50.core.exceptions import ExecutionObjectDetectedError

                raise ExecutionObjectDetectedError(f"Execution field detected in payload: {k}")
            if isinstance(v, (dict, list)):
                assert_no_execution_objects(v)
    elif isinstance(payload, list):
        for item in payload:
            assert_no_execution_objects(item)


def assert_signal_config_safe(config: AppConfig) -> None:
    """Ensure the signal configuration enforces safety invariants."""
    s = config.signals
    from binance50.core.exceptions import SignalConfigError

    if not s.execution_forbidden:
        raise SignalConfigError("execution_forbidden must be True in Phase 14")
    if not s.order_creation_forbidden:
        raise SignalConfigError("order_creation_forbidden must be True in Phase 14")
    if not s.live_trade_forbidden:
        raise SignalConfigError("live_trade_forbidden must be True in Phase 14")
    if not s.paper_trade_forbidden:
        raise SignalConfigError("paper_trade_forbidden must be True in Phase 14")
    if not s.backtest_forbidden:
        raise SignalConfigError("backtest_forbidden must be True in Phase 14")
    if not s.risk_engine_required_before_execution:
        raise SignalConfigError("risk_engine_required_before_execution must be True")


def assert_no_execution_threshold(config: AppConfig) -> None:
    """Ensure no execution thresholds are active."""
    if not config.signals.thresholds.execution_threshold_deferred:
        from binance50.core.exceptions import ExecutionThresholdForbiddenError

        raise ExecutionThresholdForbiddenError(
            "execution_threshold_deferred must be True in Phase 14"
        )


def assert_signal_candidates_safe(candidates: list[SignalCandidate], config: AppConfig) -> None:
    """Check that input candidates don't contain order intents or execution data."""
    for c in candidates:
        intent_str = c.intent.value.lower() if hasattr(c.intent, "value") else str(c.intent).lower()
        if ("execution" in intent_str or "order" in intent_str) and "no" not in intent_str:
            from binance50.core.exceptions import SignalValidationError

            raise SignalValidationError(
                f"Candidate {getattr(c, 'candidate_id', 'unknown')} has execution intent"
            )
        assert_no_execution_objects(c.model_dump())


def assert_scored_signals_safe(scored: list[ScoredSignalCandidate], config: AppConfig) -> None:
    """Check that scored signals are purely research candidates and have no execution language."""
    from binance50.signals.validators import validate_no_order_language

    for s in scored:
        intent_str = s.intent.value.lower() if hasattr(s.intent, "value") else str(s.intent).lower()
        if ("execution" in intent_str or "order" in intent_str) and "no" not in intent_str:
            from binance50.core.exceptions import SignalValidationError

            raise SignalValidationError(
                f"Scored candidate {getattr(s, 'scored_signal_id', 'unknown')} has execution intent"
            )

        assert_no_execution_objects(s.model_dump())

        if s.explanation:
            validate_no_order_language(s.explanation)


def build_signal_scoring_safety_report(config: AppConfig) -> dict[str, Any]:
    """Build a safety report for the scoring configuration."""
    report = {"config_safe": False, "no_execution_threshold": False, "errors": []}

    try:
        assert_signal_config_safe(config)
        report["config_safe"] = True
    except Exception as e:
        report["errors"].append(str(e))  # type: ignore

    try:
        assert_no_execution_threshold(config)
        report["no_execution_threshold"] = True
    except Exception as e:
        report["errors"].append(str(e))  # type: ignore

    return report
