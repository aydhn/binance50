from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Optional

from binance50.config.models import AppConfig
from .filters import BinanceSymbolFilterSnapshot


@dataclass
class ExecutionNotionalReport:
    symbol: str
    price: Optional[Decimal]
    quantity: Optional[Decimal]
    notional_usdt: Optional[Decimal]
    min_notional: Optional[Decimal]
    max_notional: Optional[Decimal]
    passed: bool
    not_applicable_reason: Optional[str]
    warnings: list[str]
    metadata: dict[str, Any]


def compute_notional(price: Optional[Decimal], quantity: Optional[Decimal]) -> Optional[Decimal]:
    if price is None or quantity is None:
        return None
    return price * quantity


def validate_min_notional_value(notional: Decimal, snapshot: BinanceSymbolFilterSnapshot, config: AppConfig) -> bool:
    min_n = snapshot.min_notional.get("minNotional") or snapshot.notional.get("minNotional")
    if not min_n:
        return True
    return notional >= min_n


def validate_max_notional_value(notional: Decimal, snapshot: BinanceSymbolFilterSnapshot, config: AppConfig) -> bool:
    max_n = snapshot.notional.get("maxNotional")
    if not max_n:
        return True
    return notional <= max_n


def build_notional_report(intent: Any, snapshot: BinanceSymbolFilterSnapshot, config: AppConfig) -> ExecutionNotionalReport:
    p = getattr(intent, 'price', None)
    q = getattr(intent, 'quantity', None)
    real_notional = compute_notional(p, q)

    passed = True
    reason = None
    min_n = snapshot.min_notional.get("minNotional") or snapshot.notional.get("minNotional")
    max_n = snapshot.notional.get("maxNotional")

    if real_notional is None:
        reason = "not_applicable_sandbox"
    else:
        if min_n and real_notional < min_n:
            passed = False
        if max_n and real_notional > max_n:
            passed = False

    warnings = []
    hn = getattr(intent, 'hypothetical_notional_usdt', None)
    if hn is not None:
        warnings.append(f"hypothetical_notional_reported: {hn}")

    return ExecutionNotionalReport(
        symbol=getattr(intent, 'symbol', 'UNKNOWN'),
        price=p,
        quantity=q,
        notional_usdt=real_notional or hn,
        min_notional=min_n,
        max_notional=max_n,
        passed=passed,
        not_applicable_reason=reason,
        warnings=warnings,
        metadata={}
    )
