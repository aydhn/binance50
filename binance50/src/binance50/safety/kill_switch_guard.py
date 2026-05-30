from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import ExecutionKillSwitchError

from binance50.execution.kill_switch import assert_kill_switch_blocks_gateway, assert_kill_switch_blocks_promotion, is_kill_switch_active


def assert_kill_switch_enabled(config: AppConfig) -> None:
    if not config.execution.kill_switch.enabled:
        raise ExecutionKillSwitchError("Kill-switch must be enabled.")


def assert_kill_switch_active_by_default(config: AppConfig) -> None:
    if not is_kill_switch_active(config):
        raise ExecutionKillSwitchError("Kill-switch must be active by default in Phase 28.")


def assert_kill_switch_blocks_gateway_config(config: AppConfig) -> None:
    # Function renamed slightly to avoid naming conflict with import
    assert_kill_switch_blocks_gateway(config)


def assert_kill_switch_blocks_promotion_config(config: AppConfig) -> None:
    assert_kill_switch_blocks_promotion(config)


def build_kill_switch_safety_report(config: AppConfig) -> dict[str, Any]:
    return {
        "enabled": config.execution.kill_switch.enabled,
        "active_by_default": config.execution.kill_switch.global_kill_switch_default_on,
        "blocks_gateway": config.execution.kill_switch.block_all_gateway_calls,
        "blocks_promotion": config.execution.kill_switch.block_intent_promotion
    }
