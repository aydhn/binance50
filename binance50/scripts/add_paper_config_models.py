import re
with open("binance50/src/binance50/config/models.py", "r") as f:
    content = f.read()

paper_models_code = """

class PaperExecutionMode(str, Enum):
    local_paper = "local_paper"

class PaperExecutionModeConfig(BaseModel):
    default_mode: PaperExecutionMode = PaperExecutionMode.local_paper
    allow_local_paper: bool = True
    allow_testnet_paper: bool = False
    allow_live: bool = False
    require_explicit_cli_command: bool = True
    auto_start_forbidden: bool = True
    background_execution_forbidden: bool = True

    @validator("allow_testnet_paper")
    def validate_testnet_paper(cls, v):
        if v:
            raise ValueError("allow_testnet_paper must be False for Phase 29 paper execution.")
        return v

    @validator("allow_live")
    def validate_live(cls, v):
        if v:
            raise ValueError("allow_live must be False for Phase 29 paper execution.")
        return v

class PaperIntentConfig(BaseModel):
    source_execution_intent_required: bool = True
    allow_sandbox_to_paper_candidate_conversion: bool = True
    require_phase28_safety_scan_passed: bool = True
    require_kill_switch_override_forbidden: bool = True
    require_source_trace: bool = True
    require_correlation_id: bool = True
    require_idempotency_key: bool = True
    reject_live_testnet_intent: bool = True
    reject_exchange_order_fields: bool = True
    reject_credentials: bool = True
    reject_signed_payload: bool = True

class PaperOrderConfig(BaseModel):
    internal_order_id_prefix: str = "paper_"
    client_order_id_forbidden: bool = True
    exchange_order_id_forbidden: bool = True
    allowed_order_types: list[str] = ["market", "limit"]
    default_order_type: str = "market"
    allowed_sides: list[str] = ["buy", "sell"]
    allowed_time_in_force: list[str] = ["gtc", "ioc", "fok"]
    default_time_in_force: str = "gtc"
    max_orders_per_run: int = 50
    max_orders_per_symbol: int = 5
    reject_unknown_symbol: bool = True
    require_local_filter_validation: bool = True
    require_quantity_validation: bool = True
    require_notional_validation: bool = True

class PaperSizingConfig(BaseModel):
    enabled: bool = True
    simulated_equity_usdt: Decimal = Field(default=Decimal("1000.0"))
    max_total_paper_exposure_pct: Decimal = Field(default=Decimal("30.0"))
    max_single_order_notional_pct: Decimal = Field(default=Decimal("5.0"))
    max_symbol_exposure_pct: Decimal = Field(default=Decimal("10.0"))
    min_order_notional_usdt: Decimal = Field(default=Decimal("5.0"))
    quantity_from_hypothetical_notional: bool = True
    quantity_rounding: str = "floor_to_step"
    price_rounding: str = "floor_to_tick"
    leverage_forbidden: bool = True
    margin_forbidden: bool = True
    futures_forbidden: bool = True

class PaperFillConfig(BaseModel):
    enabled: bool = True
    fill_source_priority: list[str] = ["local_ohlcv", "fixture_trades"]
    network_market_data_forbidden: bool = True
    market_order_fill_price: str = "next_bar_open"
    limit_order_fill_model: str = "conservative_touch"
    same_bar_fill_forbidden: bool = True
    next_bar_fill_required: bool = True
    allow_partial_fills: bool = True
    partial_fill_model: str = "liquidity_fraction_skeleton"
    max_partial_fill_ratio: Decimal = Field(default=Decimal("0.50"))
    reject_if_no_next_bar: bool = True
    expire_unfilled_after_bars: int = 3

class PaperFeeConfig(BaseModel):
    enabled: bool = True
    maker_fee_bps: Decimal = Field(default=Decimal("10.0"))
    taker_fee_bps: Decimal = Field(default=Decimal("10.0"))
    use_order_type_fee_assumption: bool = True
    fee_asset: str = "quote"
    fee_model_is_simulated: bool = True

class PaperSlippageConfig(BaseModel):
    enabled: bool = True
    default_slippage_bps: Decimal = Field(default=Decimal("2.0"))
    volatility_adjusted_slippage: bool = True
    max_slippage_bps: Decimal = Field(default=Decimal("25.0"))
    slippage_model_is_simulated: bool = True

class PaperLedgerConfig(BaseModel):
    enabled: bool = True
    starting_cash_usdt: Decimal = Field(default=Decimal("1000.0"))
    quote_asset: str = "USDT"
    allow_negative_cash: bool = False
    allow_short_spot: bool = False
    allow_margin: bool = False
    allow_futures: bool = False
    mark_to_market: bool = True
    require_event_sourcing: bool = True
    require_append_only_ledger: bool = True
    reject_manual_balance_edit: bool = True

class PaperPnLConfig(BaseModel):
    enabled: bool = True
    realized_pnl: bool = True
    unrealized_pnl: bool = True
    mark_to_market: bool = True
    compute_fees: bool = True
    compute_slippage_cost: bool = True
    compute_equity_curve: bool = True
    compute_drawdown: bool = True
    pnl_is_simulated: bool = True

class PaperLifecycleConfig(BaseModel):
    allowed_states: list[str] = [
        "paper_draft", "paper_submitted_local", "paper_accepted_local",
        "paper_partially_filled_local", "paper_filled_local", "paper_rejected_local",
        "paper_expired_local", "paper_canceled_local", "paper_archived"
    ]
    forbidden_states: list[str] = [
        "submitted_to_exchange", "accepted_by_exchange", "filled_on_exchange",
        "canceled_on_exchange", "rejected_by_exchange"
    ]
    exchange_state_forbidden: bool = True

class PaperEventConfig(BaseModel):
    enabled: bool = True
    create_local_paper_events: bool = True
    event_stream_is_local_only: bool = True
    mimic_execution_report_shape: bool = False
    exchange_execution_report_forbidden: bool = True
    require_event_id: bool = True
    require_correlation_id: bool = True

class PaperQualityConfig(BaseModel):
    reject_missing_source_intent: bool = True
    reject_missing_safety_scan: bool = True
    reject_missing_local_filter_validation: bool = True
    reject_missing_ledger_events: bool = True
    reject_missing_pnl_report: bool = True
    reject_negative_cash: bool = True
    reject_short_spot: bool = True
    reject_exchange_order_fields: bool = True
    reject_credentials: bool = True
    reject_signed_payload: bool = True
    reject_network_calls: bool = True
    reject_exchange_states: bool = True
    reject_live_or_testnet_intent: bool = True
    reject_missing_hashes: bool = True
    warn_no_orders_filled: bool = True
    warn_high_slippage: bool = True
    warn_partial_fills: bool = True

class PaperExecutionConfig(BaseModel):
    enabled: bool = True
    output_dataset_name: str = "paper_execution_runs"
    cache_enabled: bool = True
    cache_dir: str = "data/paper/cache"
    export_dir: str = "data/paper/exports"
    reports_dir: str = "data/paper/reports"
    ledger_dir: str = "data/paper/ledger"

    real_exchange_forbidden: bool = True
    testnet_exchange_forbidden: bool = True
    live_exchange_forbidden: bool = True
    api_key_forbidden: bool = True
    signed_request_forbidden: bool = True
    network_gateway_forbidden: bool = True
    binance_rest_forbidden: bool = True
    websocket_forbidden: bool = True
    order_test_endpoint_forbidden: bool = True

    mode: PaperExecutionModeConfig = Field(default_factory=PaperExecutionModeConfig)
    intent: PaperIntentConfig = Field(default_factory=PaperIntentConfig)
    order: PaperOrderConfig = Field(default_factory=PaperOrderConfig)
    sizing: PaperSizingConfig = Field(default_factory=PaperSizingConfig)
    fills: PaperFillConfig = Field(default_factory=PaperFillConfig)
    fees: PaperFeeConfig = Field(default_factory=PaperFeeConfig)
    slippage: PaperSlippageConfig = Field(default_factory=PaperSlippageConfig)
    ledger: PaperLedgerConfig = Field(default_factory=PaperLedgerConfig)
    pnl: PaperPnLConfig = Field(default_factory=PaperPnLConfig)
    lifecycle: PaperLifecycleConfig = Field(default_factory=PaperLifecycleConfig)
    events: PaperEventConfig = Field(default_factory=PaperEventConfig)
    quality: PaperQualityConfig = Field(default_factory=PaperQualityConfig)

"""
if "class PaperExecutionModeConfig(" not in content:
    # Add new models before AppConfig
    content = content.replace("class AppConfig(BaseModel):", paper_models_code + "\nclass AppConfig(BaseModel):")

    # Add paper_execution to AppConfig
    content = content.replace(
        "    execution: ExecutionConfig = Field(default_factory=ExecutionConfig)",
        "    execution: ExecutionConfig = Field(default_factory=ExecutionConfig)\n    paper_execution: PaperExecutionConfig = Field(default_factory=PaperExecutionConfig)"
    )
    with open("binance50/src/binance50/config/models.py", "w") as f:
        f.write(content)
