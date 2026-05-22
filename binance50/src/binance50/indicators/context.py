import time
from dataclasses import dataclass, field
from typing import Any

from binance50.config.models import AppConfig
from binance50.core.enums import MarketScope


@dataclass
class IndicatorContext:
    config: AppConfig
    symbol: str
    market_scope: MarketScope
    interval: str
    backend: str
    input_columns: list[str]
    output_prefix: str = ""
    now_ms: int = field(default_factory=lambda: int(time.time() * 1000))
    correlation_id: str = ""

def build_indicator_context(
    config: AppConfig,
    symbol: str,
    market_scope: MarketScope,
    interval: str,
    backend: str,
    input_columns: list[str],
    correlation_id: str = ""
) -> IndicatorContext:
    return IndicatorContext(
        config=config,
        symbol=symbol.upper(),
        market_scope=market_scope,
        interval=interval,
        backend=backend,
        input_columns=input_columns,
        correlation_id=correlation_id
    )

def context_to_metadata(context: IndicatorContext) -> dict[str, Any]:
    return {
        "symbol": context.symbol,
        "market_scope": context.market_scope.value,
        "interval": context.interval,
        "backend": context.backend,
        "now_ms": context.now_ms,
        "correlation_id": context.correlation_id,
        "input_columns_count": len(context.input_columns)
    }
