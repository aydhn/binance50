from typing import Any

from pydantic import BaseModel, Field

from binance50.regimes.models import RegimeMethod


class RegimeContext(BaseModel):
    symbol: str
    market_scope: str
    interval: str
    method: RegimeMethod
    feature_columns: list[str] = Field(default_factory=list)
    config_hash: str
    run_id: str
    correlation_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


def build_regime_context(
    symbol: str,
    market_scope: str,
    interval: str,
    method: RegimeMethod,
    config_hash: str,
    run_id: str,
) -> RegimeContext:
    return RegimeContext(
        symbol=symbol,
        market_scope=market_scope,
        interval=interval,
        method=method,
        config_hash=config_hash,
        run_id=run_id,
    )


def validate_regime_context(context: RegimeContext) -> None:
    if not context.symbol or not context.interval:
        raise ValueError("Invalid context: missing symbol or interval")


def context_to_metadata(context: RegimeContext) -> dict[str, Any]:
    return context.model_dump()
