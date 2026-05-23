from typing import Any

from pydantic import BaseModel, ConfigDict

from binance50.config.models import AppConfig


class StrategyContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    config: AppConfig
    symbol: str
    market_scope: str
    interval: str
    plugin_name: str
    feature_metadata: dict[str, Any] = {}
    run_id: str | None = None
    correlation_id: str | None = None
    now_ms: int
    config_hash: str


def build_strategy_context(
    config: AppConfig,
    symbol: str,
    market_scope: str,
    interval: str,
    plugin_name: str,
    feature_metadata: dict[str, Any] | None = None,
    run_id: str | None = None,
    correlation_id: str | None = None,
    config_hash: str = "",
) -> StrategyContext:
    import time

    return StrategyContext(
        config=config,
        symbol=symbol.upper(),
        market_scope=market_scope,
        interval=interval,
        plugin_name=plugin_name,
        feature_metadata=feature_metadata or {},
        run_id=run_id,
        correlation_id=correlation_id,
        now_ms=int(time.time() * 1000),
        config_hash=config_hash,
    )


def context_to_metadata(context: StrategyContext) -> dict[str, Any]:
    return {
        "symbol": context.symbol,
        "market_scope": context.market_scope,
        "interval": context.interval,
        "plugin_name": context.plugin_name,
        "run_id": context.run_id,
        "correlation_id": context.correlation_id,
        "config_hash": context.config_hash,
    }


def validate_strategy_context(context: StrategyContext) -> None:
    if not context.symbol.isupper():
        raise ValueError("Symbol must be uppercase")
