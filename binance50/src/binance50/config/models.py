from typing import Literal

from pydantic import BaseModel, Field, SecretStr, model_validator

from binance50.core.enums import (
    AccountDomain,
    EnvironmentProfileName,
    ExchangeName,
    MarketScope,
    PermissionLevel,
    RuntimeEnvironment,
    TradingMode,
)


class ProjectConfig(BaseModel):
    name: str = "binance50"
    version: str = "0.1.0"


class RuntimeConfig(BaseModel):
    environment_profile: EnvironmentProfileName = EnvironmentProfileName.LOCAL_PAPER_SPOT
    exchange: ExchangeName = ExchangeName.BINANCE
    environment: RuntimeEnvironment = RuntimeEnvironment.LOCAL
    trading_mode: TradingMode = TradingMode.PAPER
    market_scope: MarketScope = MarketScope.SPOT
    account_domain: AccountDomain = AccountDomain.SPOT
    timezone: str = "UTC"


class SafetyConfig(BaseModel):
    enable_live_trading: bool = False
    confirm_live_trading: bool = False
    max_symbols_initial: int = Field(default=5, ge=1, le=20)
    default_quote_asset: str = "USDT"
    allow_testnet_orders: bool = False
    allow_demo_orders: bool = False
    allow_live_orders: bool = False
    require_manual_live_unlock: bool = True
    require_mainnet_confirmation: bool = True
    readonly_mainnet_allowed: bool = True
    dry_run: bool = True
    force_paper_mode: bool = True
    disable_all_orders: bool = True
    live_unlock_phrase_required: str = "I_UNDERSTAND_REAL_MONEY_RISK"
    live_risk_ack_required: str = "I_ACCEPT_FULL_RESPONSIBILITY"
    max_daily_loss_pct: float = Field(default=1.0, ge=0.0, le=10.0)
    max_position_risk_pct: float = Field(default=0.25, ge=0.0, le=5.0)
    max_open_positions: int = Field(default=3, ge=1, le=50)
    max_orders_per_hour: int = Field(default=20, ge=1, le=500)

    @model_validator(mode="after")
    def validate_safety(self) -> "SafetyConfig":
        if not self.default_quote_asset:
            raise ValueError("Quote asset cannot be empty")
        if self.allow_live_orders and not (self.enable_live_trading and self.confirm_live_trading):
            raise ValueError(
                "allow_live_orders requires enable_live_trading and confirm_live_trading"
            )
        return self


class BinanceCredentialConfig(BaseModel):
    api_key: SecretStr | None = None
    api_secret: SecretStr | None = None
    api_key_label: str | None = None
    permission_read: bool = False
    permission_spot_trade: bool = False
    permission_futures_trade: bool = False
    permission_margin_trade: bool = False
    ip_restricted: bool = False
    allowed_ips: list[str] = Field(default_factory=list)


class TelegramCredentialConfig(BaseModel):
    bot_token: SecretStr | None = None
    chat_id: SecretStr | None = None


class CredentialsConfig(BaseModel):
    binance: BinanceCredentialConfig = Field(default_factory=BinanceCredentialConfig)
    telegram: TelegramCredentialConfig = Field(default_factory=TelegramCredentialConfig)


class LoggingConfig(BaseModel):
    level: str = "INFO"
    log_dir: str = "logs"


class DataConfig(BaseModel):
    root_dir: str = "data"


class ReportsConfig(BaseModel):
    root_dir: str = "reports"


class EndpointConfig(BaseModel):
    rest_base_url: str | None = None
    rest_fallback_urls: list[str] = Field(default_factory=list)
    websocket_market_base_url: str | None = None
    websocket_user_base_url: str | None = None


class CredentialPolicyConfig(BaseModel):
    requires_credentials: bool = False
    allows_empty_credentials: bool = True
    forbids_credentials: bool = False


class PermissionPolicyConfig(BaseModel):
    requires_read_permission: bool = False
    requires_spot_trade_permission: bool = False
    requires_futures_trade_permission: bool = False
    requires_margin_trade_permission: bool = False
    requires_ip_restriction: bool = False


class OrderPolicyConfig(BaseModel):
    allows_simulated_orders: bool = True
    allows_testnet_orders: bool = False
    allows_live_orders: bool = False


class EnvironmentProfileConfig(BaseModel):
    profile_name: EnvironmentProfileName
    exchange: ExchangeName
    runtime_environment: RuntimeEnvironment
    trading_mode: TradingMode
    market_scope: MarketScope
    account_domain: AccountDomain
    endpoints: EndpointConfig
    is_testnet: bool
    is_mainnet: bool
    is_paper: bool
    is_live: bool
    allows_real_orders: bool
    requires_api_key: bool
    requires_api_secret: bool
    requires_live_guard: bool
    supports_user_data_stream: bool
    supports_market_stream: bool
    supports_order_placement: bool
    permission_level: PermissionLevel
    notes: str | None = None

    credential_policy: CredentialPolicyConfig = Field(default_factory=CredentialPolicyConfig)
    permission_policy: PermissionPolicyConfig = Field(default_factory=PermissionPolicyConfig)
    order_policy: OrderPolicyConfig = Field(default_factory=OrderPolicyConfig)
    allowed_when_dry_run: bool = True
    allowed_when_force_paper: bool = True
    compatible_with_disable_all_orders: bool = True

    @model_validator(mode="after")
    def validate_profile(self) -> "EnvironmentProfileConfig":
        if self.exchange != ExchangeName.BINANCE:
            raise ValueError("Exchange must be binance")

        if self.is_paper and self.allows_real_orders:
            raise ValueError("Paper profiles cannot allow real orders")

        if self.permission_level == PermissionLevel.READ_ONLY and self.supports_order_placement:
            raise ValueError("Readonly profiles cannot support order placement")

        if self.is_live:
            if not self.is_mainnet:
                raise ValueError("Live profiles must be mainnet")
            if self.allows_real_orders and not self.requires_live_guard:
                raise ValueError("Live profiles that allow real orders must require live guard")
            if self.permission_level != PermissionLevel.LIVE_ORDER:
                raise ValueError("Live profiles must have live_order permission level")

        if self.is_testnet:
            if self.is_mainnet:
                raise ValueError("Testnet profiles cannot be mainnet")
            if self.permission_level not in (PermissionLevel.TEST_ORDER, PermissionLevel.READ_ONLY):
                raise ValueError(
                    "Testnet profiles must have test_order or read_only permission level"
                )

        if self.is_paper:
            if self.requires_api_key or self.requires_api_secret:
                raise ValueError("Paper profiles cannot require API credentials")
            if self.permission_level != PermissionLevel.NO_CREDENTIALS:
                raise ValueError("Paper profiles must have no_credentials permission level")

        return self


class NetworkConfig(BaseModel):
    real_network_enabled: bool = False
    request_timeout_seconds: float = Field(default=10, gt=0)
    connect_timeout_seconds: float = Field(default=5, gt=0)
    read_timeout_seconds: float = Field(default=10, gt=0)
    write_timeout_seconds: float = Field(default=10, gt=0)
    pool_timeout_seconds: float = Field(default=5, gt=0)
    max_retry_attempts: int = Field(default=3, ge=0, le=10)
    retry_enabled: bool = True
    retry_jitter_enabled: bool = True
    retry_multiplier: float = Field(default=2.0, ge=1.0)
    retry_max_delay_seconds: float = Field(default=30.0, gt=0)
    retry_on_5xx: bool = True
    retry_on_429: bool = False
    retry_on_418: bool = False
    retry_on_timeout: bool = True
    circuit_breaker_enabled: bool = True
    circuit_breaker_failure_threshold: int = Field(default=5, ge=1)
    circuit_breaker_cooldown_seconds: float = Field(default=60, gt=0)

    @model_validator(mode="after")
    def validate_network(self) -> "NetworkConfig":
        if self.real_network_enabled:
            from binance50.core.exceptions import SafetyError

            raise SafetyError("Real network is blocked in Phase 6")
        return self


class BinanceTimingConfig(BaseModel):
    recv_window_ms: int = Field(default=5000, ge=1000, le=60000)
    recv_window_max_ms: int = Field(default=60000, ge=1000, le=60000)
    timestamp_unit: Literal["milliseconds", "microseconds"] = "milliseconds"
    clock_sync_enabled: bool = False
    max_allowed_clock_drift_ms: int = Field(default=1000, ge=0, le=5000)
    clock_sync_interval_seconds: int = Field(default=300, gt=0)
    reject_if_clock_drift_unknown_for_signed: bool = True

    @model_validator(mode="after")
    def validate_timing(self) -> "BinanceTimingConfig":
        if self.recv_window_ms > self.recv_window_max_ms:
            raise ValueError("recv_window_ms cannot be greater than recv_window_max_ms")
        return self


class RateLimitConfig(BaseModel):
    enabled: bool = True
    mode: Literal["conservative", "balanced", "aggressive"] = "conservative"
    request_weight_limit_per_minute: int = 6000
    raw_request_limit_per_5_minutes: int = 61000
    order_count_limit_10s: int = 50
    order_count_limit_1m: int = 160000
    hard_stop_on_418: bool = True
    cooldown_on_429_seconds: int = Field(default=60, gt=0)
    cooldown_on_418_min_seconds: int = Field(default=120, gt=0)
    cooldown_on_418_max_seconds: int = Field(default=259200, gt=0)
    respect_retry_after_header: bool = True
    safety_usage_threshold_pct: float = Field(default=80.0, ge=0.0, le=100.0)
    critical_usage_threshold_pct: float = Field(default=95.0, ge=0.0, le=100.0)

    @model_validator(mode="after")
    def validate_rate_limit(self) -> "RateLimitConfig":
        if self.safety_usage_threshold_pct >= self.critical_usage_threshold_pct:
            raise ValueError(
                "safety_usage_threshold_pct must be less than critical_usage_threshold_pct"
            )
        if self.cooldown_on_418_max_seconds < self.cooldown_on_418_min_seconds:
            raise ValueError("cooldown_on_418_max_seconds must be >= cooldown_on_418_min_seconds")
        return self


class WebSocketLimitsConfig(BaseModel):
    spot_max_incoming_messages_per_second: int = Field(default=5, ge=1, le=5)
    spot_max_streams_per_connection: int = Field(default=1024, ge=1, le=1024)
    spot_max_connection_attempts_per_5m_per_ip: int = Field(default=300, gt=0)
    usdm_max_incoming_messages_per_second: int = Field(default=10, ge=1, le=10)
    usdm_max_streams_per_connection: int = Field(default=200, ge=1, le=200)
    max_connection_lifetime_hours: int = Field(default=24, ge=1, le=24)
    reconnect_before_disconnect_minutes: int = Field(default=10, ge=1, le=60)
    subscribe_batch_size: int = Field(default=50, gt=0)
    control_message_budget_per_second: int = Field(default=3, gt=0)


class ConnectorConfig(BaseModel):
    connection_enabled: bool = False
    mock_enabled: bool = False
    order_gateway_enabled: bool = False
    websocket_enabled: bool = False
    user_data_stream_enabled: bool = False
    request_timeout_seconds: int = Field(default=10, ge=1, le=30)
    recv_window_ms: int = Field(default=5000, ge=1000, le=60000)
    max_retry_attempts: int = Field(default=3, ge=0)
    backoff_initial_seconds: float = Field(default=0.5, gt=0)
    backoff_max_seconds: float = Field(default=8.0)
    max_connection_lifetime_hours: int = Field(default=24, ge=1, le=24)
    websocket_ping_timeout_seconds: int = Field(default=60, ge=5, le=600)
    websocket_reconnect_before_disconnect_minutes: int = Field(default=10, ge=1, le=60)
    max_incoming_messages_per_second: int = Field(default=10, ge=1, le=100)
    rate_limit_backoff_enabled: bool = True
    circuit_breaker_enabled: bool = True
    allow_real_network_in_phase5: bool = False

    @model_validator(mode="after")
    def validate_backoff(self) -> "ConnectorConfig":
        if self.backoff_max_seconds < self.backoff_initial_seconds:
            raise ValueError("backoff_max_seconds must be >= backoff_initial_seconds")
        if self.allow_real_network_in_phase5:
            from binance50.core.exceptions import ConfigValidationError

            raise ConfigValidationError("Real network is blocked in Phase 5")
        return self


class EnvironmentMatrixConfig(BaseModel):
    profiles: dict[EnvironmentProfileName, EnvironmentProfileConfig] = Field(default_factory=dict)
    default_profile: EnvironmentProfileName = EnvironmentProfileName.LOCAL_PAPER_SPOT


class UniverseScoringConfig(BaseModel):
    liquidity_weight: float = 0.35
    spread_weight: float = 0.30
    filter_quality_weight: float = 0.20
    stability_weight: float = 0.10
    preference_weight: float = 0.05
    min_score: float = Field(default=60.0, ge=0.0, le=100.0)

    @model_validator(mode="after")
    def validate_weights(self) -> "UniverseScoringConfig":
        total_weight = (
            self.liquidity_weight
            + self.spread_weight
            + self.filter_quality_weight
            + self.stability_weight
            + self.preference_weight
        )
        if not (0.99 <= total_weight <= 1.01):
            raise ValueError(f"Scoring weights must sum to 1.0 (got {total_weight})")
        return self


class UniverseConfig(BaseModel):
    enabled: bool = True
    quote_assets: list[str] = Field(default_factory=lambda: ["USDT"], min_length=1)
    default_quote_asset: str = "USDT"
    market_scopes: list[MarketScope] = Field(
        default_factory=lambda: [MarketScope.SPOT, MarketScope.USDM_FUTURES]
    )
    max_symbols_initial: int = Field(default=10, ge=5, le=20)
    min_symbols_required: int = Field(default=3, ge=1)
    max_symbols_allowed: int = Field(default=50, ge=5, le=50)
    prefer_major_symbols: bool = True
    major_symbols: list[str] = Field(default_factory=list)
    exclude_assets: list[str] = Field(default_factory=list)
    exclude_symbol_patterns: list[str] = Field(default_factory=list)
    allow_stablecoin_pairs: bool = False
    allow_leveraged_tokens: bool = False
    allow_fan_tokens: bool = False
    require_trading_status: bool = True
    require_quote_volume: bool = True
    require_book_ticker: bool = True
    require_filters: bool = True
    min_quote_volume_24h_usdt: float = Field(default=10000000.0, ge=0.0)
    min_trade_count_24h: int = Field(default=10000, ge=0)
    max_spread_bps: float = Field(default=8.0, gt=0.0)
    warning_spread_bps: float = Field(default=5.0, gt=0.0)
    min_bid_ask_qty_notional_usdt: float = Field(default=1000.0, ge=0.0)
    min_notional_ceiling_usdt: float = Field(default=25.0, ge=0.0)
    max_price_tick_pct: float = Field(default=0.5, gt=0.0)
    max_qty_step_pct: float = Field(default=1.0, gt=0.0)
    blacklist_file: str = "config/symbol_blacklist.yaml"
    whitelist_file: str = "config/symbol_whitelist.yaml"
    cache_enabled: bool = True
    cache_dir: str = "data/universe"
    cache_ttl_seconds: int = Field(default=3600, ge=60, le=86400)
    snapshot_dir: str = "data/universe/snapshots"
    scoring: UniverseScoringConfig = Field(default_factory=UniverseScoringConfig)

    @model_validator(mode="after")
    def validate_universe(self) -> "UniverseConfig":
        if self.default_quote_asset not in self.quote_assets:
            raise ValueError(
                f"default_quote_asset {self.default_quote_asset} must be in quote_assets"
            )
        if not (self.min_symbols_required <= self.max_symbols_initial <= self.max_symbols_allowed):
            raise ValueError(
                "min_symbols_required <= max_symbols_initial <= max_symbols_allowed condition failed"
            )
        if self.warning_spread_bps >= self.max_spread_bps:
            raise ValueError("warning_spread_bps must be less than max_spread_bps")
        return self


class MarketDataQualityConfig(BaseModel):
    reject_duplicate_open_time: bool = True
    reject_out_of_order: bool = True
    reject_negative_prices: bool = True
    reject_zero_or_negative_close: bool = True
    reject_high_low_inconsistency: bool = True
    reject_negative_volume: bool = True
    warn_zero_volume: bool = True
    detect_gaps: bool = True
    max_gap_ratio_pct: float = Field(default=1.0, ge=0.0, le=100.0)
    allow_weekend_crypto_continuity: bool = True
    timezone: str = "UTC"


class CachePartitioningConfig(BaseModel):
    by_market_scope: bool = True
    by_symbol: bool = True
    by_interval: bool = True


class MarketDataConfig(BaseModel):
    enabled: bool = True
    real_fetch_enabled: bool = False
    source: str = "binance_public"
    prefer_market_data_only_endpoint: bool = True
    base_data_endpoint: str = "https://data-api.binance.vision"
    spot_klines_path: str = "/api/v3/klines"
    usdm_klines_path: str = "/fapi/v1/klines"
    default_intervals: list[str] = Field(default_factory=list)
    allowed_intervals: list[str] = Field(default_factory=list, min_length=1)
    default_history_days: dict[str, int] = Field(default_factory=dict)
    spot_max_limit: int = Field(default=1000, le=1000)
    usdm_max_limit: int = Field(default=1500, le=1500)
    request_limit_safety_margin_pct: float = Field(default=90.0, ge=1.0, le=100.0)
    exclude_incomplete_last_candle: bool = True
    require_closed_candles: bool = True
    allow_partial_candle_cache: bool = False
    cache_enabled: bool = True
    cache_format: Literal["parquet", "csv", "jsonl"] = "parquet"
    cache_dir: str = "data/ohlcv"
    metadata_dir: str = "data/ohlcv/metadata"
    export_dir: str = "data/ohlcv/exports"
    cache_partitioning: CachePartitioningConfig = Field(default_factory=CachePartitioningConfig)
    incremental_enabled: bool = True
    overlap_candles_on_update: int = Field(default=2, ge=0, le=10)
    max_gap_fill_attempts: int = Field(default=3, ge=0, le=10)
    validate_after_fetch: bool = True
    validate_after_cache_load: bool = True
    min_rows_required: int = Field(default=100, ge=1)
    max_rows_per_symbol_interval: int = Field(default=2000000, gt=0)
    quality: MarketDataQualityConfig = Field(default_factory=MarketDataQualityConfig)

    @model_validator(mode="after")
    def validate_market_data(self) -> "MarketDataConfig":
        if self.real_fetch_enabled:
            from binance50.core.exceptions import ConfigValidationError

            raise ConfigValidationError(
                "real_fetch_enabled=True is blocked in Phase 8 default safety"
            )
        for inv in self.default_intervals:
            if inv not in self.allowed_intervals:
                raise ValueError(f"default_interval {inv} must be in allowed_intervals")
        for inv in self.default_intervals:
            if inv not in self.default_history_days:
                raise ValueError(f"default_history_days must cover {inv}")
        return self



from typing import Literal


class StreamLifecycleConfig(BaseModel):
    max_connection_lifetime_hours: int = Field(default=24, le=24)
    reconnect_before_disconnect_minutes: int = 10
    ping_timeout_seconds: int = 60
    pong_timeout_seconds: int = 600
    reconnect_backoff_initial_seconds: float = 1.0
    reconnect_backoff_max_seconds: float = 60.0

class StreamsConfig(BaseModel):
    enabled: bool = True
    market_stream_real_connect_enabled: bool = False
    use_combined_streams: bool = True
    default_stream_types: list[str] = Field(default_factory=lambda: ["kline", "bookTicker", "miniTicker"])
    allowed_stream_types: list[str] = Field(default_factory=lambda: [
        "kline", "miniTicker", "ticker", "bookTicker", "partialDepth",
        "diffDepth", "trade", "aggTrade", "markPrice", "forceOrder"
    ])
    default_kline_interval: str = "1m"
    allowed_kline_intervals: list[str] = Field(default_factory=lambda: [
        "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"
    ])
    max_symbols_per_stream_plan: int = Field(default=20, ge=1, le=50)
    max_streams_per_connection_spot: int = Field(default=1024, le=1024)
    max_streams_per_connection_usdm: int = Field(default=1024, le=1024)
    max_control_messages_per_second_spot: int = Field(default=5, le=5)
    max_control_messages_per_second_usdm: int = Field(default=10, le=10)
    buffer_max_events: int = Field(default=10000, ge=100, le=1_000_000)
    buffer_drop_policy: Literal["reject_new", "drop_oldest", "drop_newest"] = "reject_new"
    buffer_warn_threshold_pct: float = Field(default=80.0, ge=1.0, le=100.0)
    stale_event_threshold_seconds: int = 30
    max_event_time_skew_ms: int = 5000
    require_monotonic_event_time: bool = False
    detect_duplicate_events: bool = True
    duplicate_cache_size: int = Field(default=5000, ge=100, le=100_000)
    replay_enabled: bool = True
    replay_speed_multiplier: float = Field(default=1.0, gt=0.0)
    realtime_store_enabled: bool = True
    persist_realtime_snapshots: bool = False
    lifecycle: StreamLifecycleConfig = Field(default_factory=StreamLifecycleConfig)

    @model_validator(mode="after")
    def validate_streams(self) -> "StreamsConfig":
        if self.market_stream_real_connect_enabled:
            from binance50.core.exceptions import ConfigValidationError
            raise ConfigValidationError("market_stream_real_connect_enabled=True is blocked in Phase 9")

        for st in self.default_stream_types:
            if st not in self.allowed_stream_types:
                raise ValueError(f"default_stream_type {st} must be in allowed_stream_types")

        if self.default_kline_interval not in self.allowed_kline_intervals:
            raise ValueError(f"default_kline_interval {self.default_kline_interval} must be in allowed_kline_intervals")

        return self

class AppConfig(BaseModel):
    project: ProjectConfig = ProjectConfig()
    runtime: RuntimeConfig = RuntimeConfig()
    safety: SafetyConfig = SafetyConfig()
    credentials: CredentialsConfig = CredentialsConfig()
    logging: LoggingConfig = LoggingConfig()
    data: DataConfig = DataConfig()
    reports: ReportsConfig = ReportsConfig()
    connector: ConnectorConfig = ConnectorConfig()
    network: NetworkConfig = NetworkConfig()
    binance_timing: BinanceTimingConfig = BinanceTimingConfig()
    rate_limit: RateLimitConfig = RateLimitConfig()
    websocket_limits: WebSocketLimitsConfig = WebSocketLimitsConfig()
    environment_matrix: EnvironmentMatrixConfig = EnvironmentMatrixConfig()
    universe: UniverseConfig = UniverseConfig()
    market_data: MarketDataConfig = MarketDataConfig()
    streams: StreamsConfig = StreamsConfig()

    @model_validator(mode="after")
    def validate_live_trading(self) -> "AppConfig":
        if self.runtime.trading_mode == TradingMode.LIVE and (
            not self.safety.enable_live_trading or not self.safety.confirm_live_trading
        ):
            raise ValueError(
                "Live trading requires enable_live_trading and confirm_live_trading to be true"
            )

        if self.safety.force_paper_mode and self.runtime.trading_mode == TradingMode.LIVE:
            raise ValueError("Trading mode cannot be live when force_paper_mode is true")

        if self.safety.disable_all_orders and self.connector.order_gateway_enabled:
            raise ValueError("Order gateway cannot be enabled when disable_all_orders is true")

        if self.safety.dry_run and self.runtime.trading_mode == TradingMode.LIVE:
            raise ValueError("Trading mode cannot be live when dry_run is true")

        return self

    @property
    def selected_environment_profile(self) -> EnvironmentProfileConfig:
        profile_name = self.runtime.environment_profile
        if profile_name not in self.environment_matrix.profiles:
            raise ValueError(f"Profile {profile_name} not found in environment matrix")
        return self.environment_matrix.profiles[profile_name]
