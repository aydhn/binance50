from enum import Enum
from typing import Any

from pydantic import BaseModel


class BacktestEventType(str, Enum):
    run_started = "run_started"
    bar_opened = "bar_opened"
    bar_closed = "bar_closed"
    features_computed = "features_computed"
    strategy_evaluated = "strategy_evaluated"
    signal_scored = "signal_scored"
    regime_classified = "regime_classified"
    risk_assessed = "risk_assessed"
    simulated_fill_created = "simulated_fill_created"
    position_opened = "position_opened"
    position_closed = "position_closed"
    equity_updated = "equity_updated"
    run_completed = "run_completed"
    run_failed = "run_failed"

class BacktestRunStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    invalid = "invalid"

class BacktestPositionStatus(str, Enum):
    open = "open"
    closed = "closed"
    rejected = "rejected"

class BacktestFillModel(str, Enum):
    next_bar_open = "next_bar_open"
    next_bar_close = "next_bar_close"
    current_bar_close_for_debug_only = "current_bar_close_for_debug_only"

class BacktestIntent(str, Enum):
    simulation_only = "simulation_only"
    research_backtest = "research_backtest"
    no_order = "no_order"

class BacktestEvent(BaseModel):
    event_id: str
    run_id: str
    event_type: BacktestEventType
    symbol: str | None = None
    market_scope: str | None = None
    interval: str | None = None
    open_time: int | None = None
    event_time: int
    message: str
    metadata: dict[str, Any] | None = None
    created_at_utc: str

class BacktestFill(BaseModel):
    fill_id: str
    run_id: str
    symbol: str
    side: str
    simulated_price: float
    simulated_quantity: float
    simulated_notional_usdt: float
    simulated_fee_usdt: float
    simulated_slippage_bps: float
    fill_time: int
    source_event_id: str | None = None
    source_risk_assessment_id: str | None = None
    metadata: dict[str, Any] | None = None

class BacktestPosition(BaseModel):
    position_id: str
    run_id: str
    symbol: str
    side: str
    status: BacktestPositionStatus
    opened_at: int
    closed_at: int | None = None
    open_price: float
    close_price: float | None = None
    simulated_quantity: float
    simulated_notional_usdt: float
    fees_paid_usdt: float = 0.0
    slippage_paid_usdt: float = 0.0
    realized_pnl_usdt: float = 0.0
    unrealized_pnl_usdt: float = 0.0
    holding_bars: int = 0
    close_reason: str | None = None
    source_signal_id: str | None = None
    source_risk_assessment_id: str | None = None
    metadata: dict[str, Any] | None = None

class BacktestTrade(BaseModel):
    trade_id: str
    run_id: str
    position_id: str
    symbol: str
    interval: str
    opened_at: int
    closed_at: int
    side: str
    entry_price: float
    exit_price: float
    simulated_quantity: float
    gross_pnl_usdt: float
    net_pnl_usdt: float
    return_pct: float
    fees_usdt: float
    slippage_cost_usdt: float
    holding_bars: int
    source_signal_score: float | None = None
    source_risk_score: float | None = None
    regime_at_entry: str | None = None
    close_reason: str
    explanation: str
    metadata: dict[str, Any] | None = None

class BacktestEquityPoint(BaseModel):
    run_id: str
    open_time: int
    cash_usdt: float
    equity_usdt: float
    unrealized_pnl_usdt: float
    realized_pnl_usdt: float
    drawdown_pct: float
    open_position_count: int
    metadata: dict[str, Any] | None = None

class BacktestRunRequest(BaseModel):
    symbol: str
    market_scope: str
    interval: str
    input_ohlcv_dataset_name: str
    start_time_ms: int | None = None
    end_time_ms: int | None = None
    strategy_profile: str
    request_id: str
    correlation_id: str | None = None

class BacktestRunResult(BaseModel):
    request: BacktestRunRequest
    run_id: str
    status: BacktestRunStatus
    events: list[BacktestEvent]
    fills: list[BacktestFill]
    positions: list[BacktestPosition]
    trades: list[BacktestTrade]
    equity_curve: list[BacktestEquityPoint]
    metrics: Any | None = None # type BacktestMetrics defined later
    benchmark: Any | None = None # type BacktestBenchmarkResult
    quality_report: Any | None = None # type BacktestQualityReport
    metadata: dict[str, Any] | None = None
    success: bool
    error: str | None = None
