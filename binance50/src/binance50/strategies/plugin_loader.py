from typing import Any

from binance50.config.models import AppConfig
from binance50.strategies.base import StrategyPluginProtocol


def load_builtin_plugins(config: AppConfig) -> list[StrategyPluginProtocol]:
    # In a full implementation, these would be imported from the plugins module
    # We will instantiate them here or in their respective modules and return them.
    from binance50.strategies.plugins.composite_skeleton import CompositeSkeletonPlugin
    from binance50.strategies.plugins.divergence_candidate import DivergenceCandidatePlugin
    from binance50.strategies.plugins.mean_reversion import MeanReversionPlugin
    from binance50.strategies.plugins.momentum_continuation import MomentumContinuationPlugin
    from binance50.strategies.plugins.mtf_confirmation import MTFConfirmationPlugin
    from binance50.strategies.plugins.pattern_candidate import PatternCandidatePlugin
    from binance50.strategies.plugins.trend_following import TrendFollowingPlugin
    from binance50.strategies.plugins.volatility_breakout import VolatilityBreakoutPlugin
    from binance50.strategies.plugins.volume_confirmation import VolumeConfirmationPlugin

    plugins = [
        TrendFollowingPlugin(),
        MeanReversionPlugin(),
        MomentumContinuationPlugin(),
        VolatilityBreakoutPlugin(),
        VolumeConfirmationPlugin(),
        DivergenceCandidatePlugin(),
        MTFConfirmationPlugin(),
        PatternCandidatePlugin(),
        CompositeSkeletonPlugin(),
    ]
    return plugins


def discover_external_plugins(config: AppConfig) -> list[StrategyPluginProtocol]:
    # Discovery of external plugins is disabled in Phase 13
    return []


def build_plugin_load_report(config: AppConfig) -> dict[str, Any]:
    builtins = load_builtin_plugins(config)
    return {
        "builtin_count": len(builtins),
        "external_count": 0,
        "plugins_loaded": [p.name for p in builtins],
    }
