import uuid
from decimal import Decimal
from typing import Optional
from datetime import datetime, timezone
from binance50.config.models import AppConfig
from binance50.paper.models import PaperOrder, PaperOrderSide, PaperFill, PaperLedgerEvent, PaperBalanceSnapshot, PaperPosition
from binance50.core.exceptions import PaperLedgerError

class PaperLedger:
    def __init__(self):
        self.events: list[PaperLedgerEvent] = []
        self.current_cash: Decimal = Decimal("0.0")

    def initialize(self, starting_cash_usdt: Decimal, config: AppConfig):
        self.current_cash = starting_cash_usdt
        event = PaperLedgerEvent(
            ledger_event_id=f"ledger_{uuid.uuid4().hex[:8]}",
            event_type="initialization",
            asset=config.paper_execution.ledger.quote_asset,
            cash_delta_usdt=starting_cash_usdt,
            asset_delta=Decimal("0.0"),
            fee_delta_usdt=Decimal("0.0"),
            equity_usdt=starting_cash_usdt,
            event_time_utc=datetime.now(timezone.utc),
            correlation_id="init"
        )
        self.events.append(event)

    def apply_fill(self, fill: PaperFill, order: PaperOrder, config: AppConfig) -> list[PaperLedgerEvent]:
        new_events = []

        # Calculate cash delta
        if order.side == PaperOrderSide.buy:
            cash_delta = -(fill.gross_amount_usdt + fill.fee_usdt + fill.slippage_cost_usdt)
            asset_delta = fill.fill_quantity
        else:
            cash_delta = fill.gross_amount_usdt - fill.fee_usdt - fill.slippage_cost_usdt
            asset_delta = -fill.fill_quantity

        self.current_cash += cash_delta

        if not config.paper_execution.ledger.allow_negative_cash and self.current_cash < 0:
            raise PaperLedgerError(f"Negative cash is forbidden: {self.current_cash}")

        event = PaperLedgerEvent(
            ledger_event_id=f"ledger_{uuid.uuid4().hex[:8]}",
            paper_order_id=order.paper_order_id,
            event_type="fill",
            symbol=order.symbol,
            asset=order.symbol.replace("USDT", ""), # simplified base asset logic
            cash_delta_usdt=cash_delta,
            asset_delta=asset_delta,
            fee_delta_usdt=fill.fee_usdt,
            equity_usdt=self.current_cash, # Will be updated by MTM later
            event_time_utc=fill.fill_open_time,
            correlation_id=order.correlation_id
        )
        self.events.append(event)
        new_events.append(event)

        return new_events

    def apply_fee(self, fill: PaperFill, config: AppConfig) -> PaperLedgerEvent:
        pass # simplified into apply_fill for now

    def mark_to_market(self, positions: list[PaperPosition], prices: dict[str, Decimal], config: AppConfig) -> PaperBalanceSnapshot:
        total_equity = self.current_cash
        for pos in positions:
            if pos.symbol in prices:
                total_equity += pos.quantity * prices[pos.symbol]

        return PaperBalanceSnapshot(
            snapshot_id=f"snap_{uuid.uuid4().hex[:8]}",
            cash_usdt=self.current_cash,
            equity_usdt=total_equity,
            total_fee_usdt=sum(e.fee_delta_usdt for e in self.events),
            total_slippage_cost_usdt=Decimal("0.0"),
            open_position_count=len([p for p in positions if p.quantity > 0]),
            created_at_utc=datetime.now(timezone.utc)
        )

    def list_events(self) -> list[PaperLedgerEvent]:
        return self.events

    def validate_append_only(self) -> None:
        pass

    def build_ledger_report(self) -> dict:
        return {"event_count": len(self.events), "current_cash": str(self.current_cash)}
