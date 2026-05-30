from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field


class PaperExecutionMode(str, Enum):
    local_paper = "local_paper"

class PaperOrderSide(str, Enum):
    buy = "buy"
    sell = "sell"

class PaperOrderType(str, Enum):
    market = "market"
    limit = "limit"

class PaperTimeInForce(str, Enum):
    gtc = "gtc"
    ioc = "ioc"
    fok = "fok"

class PaperOrderStatus(str, Enum):
    paper_draft = "paper_draft"
    paper_submitted_local = "paper_submitted_local"
    paper_accepted_local = "paper_accepted_local"
    paper_partially_filled_local = "paper_partially_filled_local"
    paper_filled_local = "paper_filled_local"
    paper_rejected_local = "paper_rejected_local"
    paper_expired_local = "paper_expired_local"
    paper_canceled_local = "paper_canceled_local"
    paper_archived = "paper_archived"

class PaperFillStatus(str, Enum):
    no_fill = "no_fill"
    partial_fill = "partial_fill"
    full_fill = "full_fill"

class PaperEventType(str, Enum):
    paper_order_created = "paper_order_created"
    paper_order_validated = "paper_order_validated"
    paper_order_submitted_local = "paper_order_submitted_local"
    paper_order_accepted_local = "paper_order_accepted_local"
    paper_order_partially_filled_local = "paper_order_partially_filled_local"
    paper_order_filled_local = "paper_order_filled_local"
    paper_order_rejected_local = "paper_order_rejected_local"
    paper_order_expired_local = "paper_order_expired_local"
    paper_order_canceled_local = "paper_order_canceled_local"
    paper_ledger_updated = "paper_ledger_updated"
    paper_pnl_updated = "paper_pnl_updated"

class PaperOrder(BaseModel):
    paper_order_id: str
    source_intent_id: str
    source_run_id: str
    symbol: str
    market_scope: str
    interval: str
    side: PaperOrderSide
    order_type: PaperOrderType
    time_in_force: PaperTimeInForce = PaperTimeInForce.gtc
    status: PaperOrderStatus = PaperOrderStatus.paper_draft
    requested_notional_usdt: Decimal
    requested_quantity: Decimal
    limit_price: Optional[Decimal] = None
    filled_quantity: Decimal = Field(default=Decimal("0.0"))
    avg_fill_price: Optional[Decimal] = None
    gross_cost_usdt: Decimal = Field(default=Decimal("0.0"))
    fee_usdt: Decimal = Field(default=Decimal("0.0"))
    slippage_cost_usdt: Decimal = Field(default=Decimal("0.0"))
    net_cost_usdt: Decimal = Field(default=Decimal("0.0"))
    created_open_time: datetime
    submitted_at_utc: Optional[datetime] = None
    updated_at_utc: Optional[datetime] = None
    correlation_id: str
    idempotency_key: str
    source_trace: str
    explanation: str
    metadata: dict[str, Any] = Field(default_factory=dict)

class PaperFill(BaseModel):
    paper_fill_id: str
    paper_order_id: str
    symbol: str
    side: PaperOrderSide
    fill_status: PaperFillStatus
    fill_open_time: datetime
    fill_price: Decimal
    fill_quantity: Decimal
    gross_amount_usdt: Decimal
    fee_usdt: Decimal
    slippage_bps: Decimal
    slippage_cost_usdt: Decimal
    liquidity_fraction: Decimal
    metadata: dict[str, Any] = Field(default_factory=dict)

class PaperLedgerEvent(BaseModel):
    ledger_event_id: str
    paper_order_id: Optional[str] = None
    event_type: str
    symbol: Optional[str] = None
    asset: str
    cash_delta_usdt: Decimal
    asset_delta: Decimal
    fee_delta_usdt: Decimal
    realized_pnl_delta_usdt: Decimal = Field(default=Decimal("0.0"))
    unrealized_pnl_usdt: Decimal = Field(default=Decimal("0.0"))
    equity_usdt: Decimal
    event_time_utc: datetime
    correlation_id: str
    metadata: dict[str, Any] = Field(default_factory=dict)

class PaperBalanceSnapshot(BaseModel):
    snapshot_id: str
    cash_usdt: Decimal
    equity_usdt: Decimal
    total_fee_usdt: Decimal
    total_slippage_cost_usdt: Decimal
    open_position_count: int
    created_at_utc: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)

class PaperPosition(BaseModel):
    position_id: str
    symbol: str
    quantity: Decimal
    avg_entry_price: Decimal
    market_price: Decimal
    unrealized_pnl_usdt: Decimal = Field(default=Decimal("0.0"))
    realized_pnl_usdt: Decimal = Field(default=Decimal("0.0"))
    total_fees_usdt: Decimal = Field(default=Decimal("0.0"))
    total_slippage_usdt: Decimal = Field(default=Decimal("0.0"))
    updated_at_utc: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)

class PaperExecutionRunRequest(BaseModel):
    symbol: str
    market_scope: str
    interval: str
    execution_safety_run_id: str
    portfolio_construction_run_id: Optional[str] = None
    start_time_ms: int
    end_time_ms: int
    request_id: str
    correlation_id: str

class PaperExecutionRunResult(BaseModel):
    request: PaperExecutionRunRequest
    run_id: str
    mode: PaperExecutionMode = PaperExecutionMode.local_paper
    paper_orders: list[PaperOrder] = Field(default_factory=list)
    paper_fills: list[PaperFill] = Field(default_factory=list)
    ledger_events: list[PaperLedgerEvent] = Field(default_factory=list)
    balance_snapshots: list[PaperBalanceSnapshot] = Field(default_factory=list)
    positions: list[PaperPosition] = Field(default_factory=list)
    pnl_report: dict[str, Any] = Field(default_factory=dict)
    quality_report: dict[str, Any] = Field(default_factory=dict)
    reproducibility_report: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None
