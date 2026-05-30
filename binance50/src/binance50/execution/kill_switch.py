from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import ExecutionKillSwitchError


@dataclass
class ExecutionKillSwitchReport:
    enabled: bool
    active: bool
    blocks_gateway_calls: bool
    blocks_intent_promotion: bool
    blocks_testnet_live_modes: bool
    reason: str
    generated_at_utc: datetime
    metadata: dict[str, Any]


def is_kill_switch_active(config: AppConfig) -> bool:
    return config.execution.kill_switch.enabled and config.execution.kill_switch.global_kill_switch_default_on


def assert_kill_switch_blocks_gateway(config: AppConfig) -> None:
    if is_kill_switch_active(config) and config.execution.kill_switch.block_all_gateway_calls:
        raise ExecutionKillSwitchError("Kill-switch is active. Gateway calls are blocked.")


def assert_kill_switch_blocks_promotion(config: AppConfig) -> None:
    if is_kill_switch_active(config) and config.execution.kill_switch.block_intent_promotion:
        raise ExecutionKillSwitchError("Kill-switch is active. Intent promotion is blocked.")


def build_kill_switch_report(config: AppConfig) -> ExecutionKillSwitchReport:
    active = is_kill_switch_active(config)
    reason = "Phase 28 default hard block" if active else "Kill-switch disabled"

    return ExecutionKillSwitchReport(
        enabled=config.execution.kill_switch.enabled,
        active=active,
        blocks_gateway_calls=config.execution.kill_switch.block_all_gateway_calls,
        blocks_intent_promotion=config.execution.kill_switch.block_intent_promotion,
        blocks_testnet_live_modes=config.execution.kill_switch.block_testnet_live_modes,
        reason=reason,
        generated_at_utc=datetime.now(timezone.utc),
        metadata={}
    )
