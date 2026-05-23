from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.strategies.models import StrategyRunResult
from binance50.strategies.registry import StrategyRegistry


def assert_strategy_config_safe(config: AppConfig) -> None:
    s = config.strategies
    from binance50.core.exceptions import StrategyConfigError

    if not s.execution_forbidden:
        raise StrategyConfigError("execution_forbidden must be True")
    if not s.order_creation_forbidden:
        raise StrategyConfigError("order_creation_forbidden must be True")
    if not s.live_trade_forbidden:
        raise StrategyConfigError("live_trade_forbidden must be True")
    if not s.paper_trade_forbidden:
        raise StrategyConfigError("paper_trade_forbidden must be True")
    if not s.backtest_forbidden:
        raise StrategyConfigError("backtest_forbidden must be True")
    if s.candidate.allow_actionable_order_language:
        raise StrategyConfigError("allow_actionable_order_language must be False")


def assert_strategy_input_safe(df: pd.DataFrame, config: AppConfig) -> None:
    from binance50.strategies.validators import (
        validate_no_execution_columns,
        validate_no_future_target_label_columns,
    )

    validate_no_execution_columns(df)
    validate_no_future_target_label_columns(df)


def assert_strategy_output_safe(result: StrategyRunResult, config: AppConfig) -> None:
    from binance50.safety.signal_candidate_guard import assert_candidates_safe

    assert_candidates_safe(result.candidates, config)


def assert_strategy_plugins_safe(registry: StrategyRegistry, config: AppConfig) -> None:
    for plugin in registry.list_plugins():
        for attr in dir(plugin):
            if attr.lower() in ("execute", "order", "trade", "place_order", "open_position"):
                from binance50.core.exceptions import StrategyConfigError

                raise StrategyConfigError(
                    f"Plugin {plugin.name} exposes forbidden execution method: {attr}"
                )


def assert_no_execution_objects(payload: Any) -> None:
    if isinstance(payload, dict):
        keys = list(payload.keys())
        for k in keys:
            kl = k.lower()
            if kl in (
                "order_id",
                "quantity",
                "leverage",
                "entry_price",
                "exit_price",
                "take_profit",
                "stop_loss",
            ):
                from binance50.core.exceptions import ExecutionObjectDetectedError

                raise ExecutionObjectDetectedError(f"Execution object detected in payload: {k}")
    elif hasattr(payload, "model_dump"):
        assert_no_execution_objects(payload.model_dump())


def build_strategy_safety_report(
    config: AppConfig, registry: StrategyRegistry | None = None
) -> dict[str, Any]:
    report = {"config_safe": False, "input_safe": "N/A", "plugins_safe": "N/A", "errors": []}

    try:
        assert_strategy_config_safe(config)
        report["config_safe"] = True
    except Exception as e:
        report["errors"].append(str(e))

    if registry:
        try:
            assert_strategy_plugins_safe(registry, config)
            report["plugins_safe"] = True
        except Exception as e:
            report["plugins_safe"] = False
            report["errors"].append(str(e))

    return report
