from typing import Any

from binance50.config.models import AppConfig
from binance50.signals.models import ConfluenceGroup


def assert_confluence_config_safe(config: AppConfig) -> None:
    """Check that confluence rules don't bypass safety caps."""
    c = config.signals.confluence
    from binance50.core.exceptions import SignalConfigError

    if c.max_confluence_score > 100.0:
        raise SignalConfigError("max_confluence_score cannot exceed 100.0")

    if c.pattern_confirmation_bonus > 5.0:
        raise SignalConfigError("pattern_confirmation_bonus should remain low (< 5.0)")


def assert_conflict_policy_safe(config: AppConfig) -> None:
    """Check that conflict policies are configured safely."""
    c = config.signals.conflicts
    from binance50.core.exceptions import SignalConfigError

    if c.max_conflict_penalty <= 0:
        raise SignalConfigError("max_conflict_penalty must be greater than 0")

    if c.same_plugin_conflict_penalty < c.bearish_bullish_conflict_penalty:
        raise SignalConfigError("same_plugin_conflict_penalty should generally be >= bearish_bullish_conflict_penalty")


def assert_confluence_groups_safe(groups: list[ConfluenceGroup], config: AppConfig) -> None:
    """Ensure generated confluence groups adhere to limits."""
    for g in groups:
        if g.confluence_score > config.signals.confluence.max_confluence_score:
            from binance50.core.exceptions import SignalConfluenceError
            raise SignalConfluenceError(f"Group {g.group_id} exceeds max confluence score")


def build_confluence_safety_report(config: AppConfig) -> dict[str, Any]:
    """Build a safety report for the confluence and conflict configuration."""
    report = {
        "confluence_config_safe": False,
        "conflict_policy_safe": False,
        "errors": []
    }

    try:
        assert_confluence_config_safe(config)
        report["confluence_config_safe"] = True
    except Exception as e:
        report["errors"].append(str(e)) # type: ignore

    try:
        assert_conflict_policy_safe(config)
        report["conflict_policy_safe"] = True
    except Exception as e:
        report["errors"].append(str(e)) # type: ignore

    return report
