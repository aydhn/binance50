from decimal import Decimal
from binance50.config.models import AppConfig
from binance50.paper.models import PaperBalanceSnapshot
from binance50.core.exceptions import PaperBalanceError

def compute_cash_after_buy(cash: Decimal, gross_cost: Decimal, fee: Decimal) -> Decimal:
    return cash - gross_cost - fee

def compute_cash_after_sell(cash: Decimal, gross_proceeds: Decimal, fee: Decimal) -> Decimal:
    return cash + gross_proceeds - fee

def build_balance_snapshot(ledger_events: list, positions: list, config: AppConfig) -> PaperBalanceSnapshot:
    pass # mostly handled in ledger mark_to_market

def validate_balance_snapshot(snapshot: PaperBalanceSnapshot, config: AppConfig) -> None:
    if not config.paper_execution.ledger.allow_negative_cash and snapshot.cash_usdt < 0:
        raise PaperBalanceError(f"Negative cash in snapshot: {snapshot.cash_usdt}")
