import re
from typing import Literal

from pydantic import BaseModel, Field, SecretStr, field_validator, model_validator

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
    default_stream_types: list[str] = Field(
        default_factory=lambda: ["kline", "bookTicker", "miniTicker"]
    )
    allowed_stream_types: list[str] = Field(
        default_factory=lambda: [
            "kline",
            "miniTicker",
            "ticker",
            "bookTicker",
            "partialDepth",
            "diffDepth",
            "trade",
            "aggTrade",
            "markPrice",
            "forceOrder",
        ]
    )
    default_kline_interval: str = "1m"
    allowed_kline_intervals: list[str] = Field(
        default_factory=lambda: [
            "1m",
            "3m",
            "5m",
            "15m",
            "30m",
            "1h",
            "2h",
            "4h",
            "6h",
            "8h",
            "12h",
            "1d",
            "3d",
            "1w",
            "1M",
        ]
    )
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

            raise ConfigValidationError(
                "market_stream_real_connect_enabled=True is blocked in Phase 9"
            )

        for st in self.default_stream_types:
            if st not in self.allowed_stream_types:
                raise ValueError(f"default_stream_type {st} must be in allowed_stream_types")

        if self.default_kline_interval not in self.allowed_kline_intervals:
            raise ValueError(
                f"default_kline_interval {self.default_kline_interval} must be in allowed_kline_intervals"
            )

        return self


from typing import Literal


class ParquetStorageConfig(BaseModel):
    enabled: bool = True
    compression: Literal["zstd", "snappy", "gzip", "brotli", "none"] = "zstd"
    fallback_compression: Literal["zstd", "snappy", "gzip", "brotli", "none"] = "snappy"
    use_dictionary: bool = True
    write_statistics: bool = True
    row_group_size: int = Field(default=100000, gt=0)
    max_rows_per_file: int = Field(default=500000, gt=0)
    partition_style: Literal["hive", "directory"] = "hive"
    schema_validation: bool = True
    atomic_write: bool = True
    temp_write_suffix: str = ".tmp"
    allow_overwrite: bool = False
    allow_append: bool = True
    allow_upsert: bool = True

    @model_validator(mode="after")
    def validate_parquet(self) -> "ParquetStorageConfig":
        if self.max_rows_per_file <= self.row_group_size:
            raise ValueError("max_rows_per_file must be greater than row_group_size")
        return self


class SQLiteStorageConfig(BaseModel):
    enabled: bool = True
    journal_mode: Literal["WAL", "DELETE", "TRUNCATE", "PERSIST", "MEMORY", "OFF"] = "WAL"
    synchronous: Literal["OFF", "NORMAL", "FULL", "EXTRA"] = "NORMAL"
    foreign_keys: bool = True
    busy_timeout_ms: int = Field(default=5000, ge=100, le=60000)
    integrity_check_on_start: bool = True
    quick_check_on_doctor: bool = True
    vacuum_on_compaction: bool = False
    backup_before_migration: bool = True


class StoragePartitioningConfig(BaseModel):
    by_market_scope: bool = True
    by_symbol: bool = True
    by_interval: bool = True
    by_year: bool = True
    by_month: bool = True
    by_day: bool = False


class StorageDatasetsConfig(BaseModel):
    ohlcv_dataset_name: str = "ohlcv"
    universe_dataset_name: str = "universe_selection"
    stream_events_dataset_name: str = "stream_events"
    quality_dataset_name: str = "quality_reports"
    allowed_dataset_names: list[str] = Field(
        default_factory=lambda: [
            "ohlcv",
            "universe_selection",
            "stream_events",
            "quality_reports",
            "feature_store_future",
            "backtest_results_future",
        ],
        min_length=1,
    )

    @model_validator(mode="after")
    def validate_datasets(self) -> "StorageDatasetsConfig":
        for name in self.allowed_dataset_names:
            if not re.match(r"^[a-z0-9_]+$", name):
                raise ValueError(f"dataset name {name} must be a safe slug")
        return self


class StorageIntegrityConfig(BaseModel):
    compute_file_hash: bool = True
    compute_dataframe_hash: bool = True
    verify_after_write: bool = True
    verify_before_read: bool = True
    reject_schema_drift: bool = True
    reject_duplicate_primary_keys: bool = True
    reject_empty_dataset: bool = True


class StorageRetentionConfig(BaseModel):
    enabled: bool = False
    max_versions_per_dataset: int = Field(default=20, gt=0)
    keep_latest_versions: int = Field(default=5, gt=0)
    archive_old_versions: bool = True
    delete_archived_after_days: int = Field(default=365, ge=0)

    @model_validator(mode="after")
    def validate_retention(self) -> "StorageRetentionConfig":
        if self.max_versions_per_dataset < self.keep_latest_versions:
            raise ValueError("max_versions_per_dataset must be >= keep_latest_versions")
        return self


class StorageBackupConfig(BaseModel):
    enabled: bool = True
    backup_catalog: bool = True
    backup_manifests: bool = True
    backup_parquet_metadata_only: bool = True
    max_backups: int = Field(default=20, ge=1, le=100)


class StorageSafetyConfig(BaseModel):
    allow_delete: bool = False
    allow_destructive_migration: bool = False
    require_backup_before_migration: bool = True
    block_paths_outside_project: bool = True
    block_secret_columns: bool = True
    block_unknown_dataset_names: bool = True


class StorageConfig(BaseModel):
    enabled: bool = True
    root_dir: str = "data/warehouse"
    parquet_root_dir: str = "data/warehouse/parquet"
    sqlite_catalog_path: str = "data/warehouse/catalog/binance50_catalog.sqlite"
    manifest_dir: str = "data/warehouse/manifests"
    reports_dir: str = "data/warehouse/reports"
    backups_dir: str = "data/warehouse/backups"
    exports_dir: str = "data/warehouse/exports"
    temp_dir: str = "data/warehouse/tmp"
    lock_dir: str = "data/warehouse/locks"

    parquet: ParquetStorageConfig = Field(default_factory=ParquetStorageConfig)
    sqlite: SQLiteStorageConfig = Field(default_factory=SQLiteStorageConfig)
    partitioning: StoragePartitioningConfig = Field(default_factory=StoragePartitioningConfig)
    datasets: StorageDatasetsConfig = Field(default_factory=StorageDatasetsConfig)
    integrity: StorageIntegrityConfig = Field(default_factory=StorageIntegrityConfig)
    retention: StorageRetentionConfig = Field(default_factory=StorageRetentionConfig)
    backup: StorageBackupConfig = Field(default_factory=StorageBackupConfig)
    safety: StorageSafetyConfig = Field(default_factory=StorageSafetyConfig)


class IndicatorWarmupPolicyConfig(BaseModel):
    keep_warmup_rows: bool = True
    mark_warmup_rows: bool = True
    min_valid_ratio: float = Field(default=0.70, ge=0.0, le=1.0)


class MacdConfig(BaseModel):
    enabled: bool = True
    fast: int = Field(default=12, gt=1)
    slow: int = Field(default=26, gt=1)
    signal: int = Field(default=9, gt=1)


class AdxConfig(BaseModel):
    enabled: bool = True
    period: int = Field(default=14, gt=1)


class AroonConfig(BaseModel):
    enabled: bool = True
    period: int = Field(default=14, gt=1)


class IndicatorTrendConfig(BaseModel):
    enabled: bool = True
    sma_periods: list[int] = Field(default_factory=lambda: [9, 20, 50, 100, 200])
    ema_periods: list[int] = Field(default_factory=lambda: [9, 12, 20, 26, 50, 100, 200])
    wma_periods: list[int] = Field(default_factory=lambda: [9, 20, 50])
    dema_periods: list[int] = Field(default_factory=lambda: [20, 50])
    tema_periods: list[int] = Field(default_factory=lambda: [20, 50])
    macd: MacdConfig = Field(default_factory=MacdConfig)
    adx: AdxConfig = Field(default_factory=AdxConfig)
    aroon: AroonConfig = Field(default_factory=AroonConfig)


class StochasticConfig(BaseModel):
    enabled: bool = True
    k_period: int = Field(default=14, gt=1)
    d_period: int = Field(default=3, gt=0)
    smooth_k: int = Field(default=3, gt=0)


class StochRsiConfig(BaseModel):
    enabled: bool = True
    rsi_period: int = Field(default=14, gt=1)
    stoch_period: int = Field(default=14, gt=1)
    k_period: int = Field(default=3, gt=0)
    d_period: int = Field(default=3, gt=0)


class IndicatorMomentumConfig(BaseModel):
    enabled: bool = True
    rsi_periods: list[int] = Field(default_factory=lambda: [7, 14, 21])
    stochastic: StochasticConfig = Field(default_factory=StochasticConfig)
    stoch_rsi: StochRsiConfig = Field(default_factory=StochRsiConfig)
    roc_periods: list[int] = Field(default_factory=lambda: [5, 10, 20])
    mom_periods: list[int] = Field(default_factory=lambda: [5, 10, 20])
    cci_periods: list[int] = Field(default_factory=lambda: [14, 20])
    willr_periods: list[int] = Field(default_factory=lambda: [14])


class BollingerConfig(BaseModel):
    enabled: bool = True
    period: int = Field(default=20, gt=1)
    stddev: float = Field(default=2.0, gt=0.0)


class KeltnerConfig(BaseModel):
    enabled: bool = True
    period: int = Field(default=20, gt=1)
    atr_period: int = Field(default=14, gt=1)
    multiplier: float = Field(default=2.0, gt=0.0)


class DonchianConfig(BaseModel):
    enabled: bool = True
    period: int = Field(default=20, gt=1)


class IndicatorVolatilityConfig(BaseModel):
    enabled: bool = True
    atr_periods: list[int] = Field(default_factory=lambda: [14, 21])
    natr_periods: list[int] = Field(default_factory=lambda: [14])
    bollinger: BollingerConfig = Field(default_factory=BollingerConfig)
    keltner: KeltnerConfig = Field(default_factory=KeltnerConfig)
    donchian: DonchianConfig = Field(default_factory=DonchianConfig)
    rolling_std_periods: list[int] = Field(default_factory=lambda: [10, 20, 50])


class VwapConfig(BaseModel):
    enabled: bool = True
    session_mode: str = "rolling"
    rolling_period: int = Field(default=20, gt=1)


class IndicatorVolumeConfig(BaseModel):
    enabled: bool = True
    obv: bool = True
    vwap: VwapConfig = Field(default_factory=VwapConfig)
    mfi_periods: list[int] = Field(default_factory=lambda: [14])
    cmf_periods: list[int] = Field(default_factory=lambda: [20])
    adl: bool = True
    volume_sma_periods: list[int] = Field(default_factory=lambda: [20, 50])
    volume_ema_periods: list[int] = Field(default_factory=lambda: [20])


class IndicatorTransformsConfig(BaseModel):
    enabled: bool = True
    returns_periods: list[int] = Field(default_factory=lambda: [1, 3, 5, 10])
    log_returns: bool = True
    hl_range: bool = True
    oc_change: bool = True
    typical_price: bool = True
    weighted_close: bool = True
    median_price: bool = True


class IndicatorQualityConfig(BaseModel):
    reject_all_nan_indicator: bool = True
    reject_constant_indicator: bool = False
    warn_high_nan_ratio: bool = True
    max_nan_ratio: float = Field(default=0.40, ge=0.0, le=1.0)
    detect_inf: bool = True
    detect_extreme_values: bool = True
    extreme_zscore_threshold: float = Field(default=20.0, gt=0.0)


class IndicatorsConfig(BaseModel):
    enabled: bool = True
    default_backend: str = "native"
    allowed_backends: list[str] = Field(
        default_factory=lambda: ["native", "talib_optional", "pandas_ta_optional"]
    )
    fail_if_optional_backend_missing: bool = False
    input_source_priority: list[str] = Field(
        default_factory=lambda: ["warehouse", "market_data_cache", "fixture"]
    )
    output_dataset_name: str = "indicators"
    cache_enabled: bool = True
    cache_dir: str = "data/indicators"
    export_dir: str = "data/indicators/exports"
    require_closed_candles: bool = True
    drop_incomplete_last_candle: bool = True
    prevent_lookahead_bias: bool = True
    enforce_monotonic_time: bool = True
    reject_duplicate_open_time: bool = True
    min_rows_required: int = Field(default=100, ge=10)
    max_columns_allowed: int = Field(default=500, ge=10, le=5000)
    max_indicator_specs_per_run: int = Field(default=100, ge=1, le=1000)
    float_precision: Literal["float32", "float64"] = "float64"
    fill_policy: Literal["none", "ffill", "bfill", "zero"] = "none"
    warmup_policy: IndicatorWarmupPolicyConfig = Field(default_factory=IndicatorWarmupPolicyConfig)
    default_periods: dict[str, int] = Field(
        default_factory=lambda: {"short": 9, "medium": 14, "long": 21, "slow": 50, "very_slow": 200}
    )
    trend: IndicatorTrendConfig = Field(default_factory=IndicatorTrendConfig)
    momentum: IndicatorMomentumConfig = Field(default_factory=IndicatorMomentumConfig)
    volatility: IndicatorVolatilityConfig = Field(default_factory=IndicatorVolatilityConfig)
    volume: IndicatorVolumeConfig = Field(default_factory=IndicatorVolumeConfig)
    transforms: IndicatorTransformsConfig = Field(default_factory=IndicatorTransformsConfig)
    quality: IndicatorQualityConfig = Field(default_factory=IndicatorQualityConfig)


class PivotConfig(BaseModel):
    enabled: bool = True
    method: Literal["causal_window"] = "causal_window"
    left_window: int = Field(default=3, ge=1)
    min_prominence_pct: float = Field(default=0.10, ge=0.0)
    min_distance_bars: int = Field(default=3, ge=1)
    use_centered_window: bool = False
    allow_repainting: bool = False
    confirm_after_bars: int = 0
    max_pivots_per_series: int = 5000

    @field_validator("use_centered_window")
    @classmethod
    def validate_use_centered_window(cls, v: bool) -> bool:
        if v:
            raise ValueError("use_centered_window must be False in Phase 12")
        return v

    @field_validator("allow_repainting")
    @classmethod
    def validate_allow_repainting(cls, v: bool) -> bool:
        if v:
            raise ValueError("allow_repainting must be False in Phase 12")
        return v

    @field_validator("confirm_after_bars")
    @classmethod
    def validate_confirm_after_bars(cls, v: int) -> int:
        if v > 0:
            raise ValueError("confirm_after_bars must be 0 in Phase 12 (no repainting allowed)")
        return v


class DivergenceConfig(BaseModel):
    enabled: bool = True
    lookback_bars: int = Field(default=100, ge=1)
    max_pivot_pair_distance: int = Field(default=50, ge=1)
    min_pivot_distance: int = Field(default=3, ge=1)
    price_source: str = "close"
    indicator_sources: list[str] = Field(default_factory=lambda: ["mom_rsi_14"], min_length=1)
    detect_regular: bool = True
    detect_hidden: bool = True
    require_price_pivot: bool = True
    require_indicator_pivot: bool = True
    min_indicator_delta_pct: float = Field(default=0.05, ge=0.0)
    min_price_delta_pct: float = Field(default=0.05, ge=0.0)
    score_enabled: bool = True
    max_divergence_score: float = 100.0
    output_flags: bool = True
    output_scores: bool = True

    @model_validator(mode="after")
    def validate_distances(self) -> "DivergenceConfig":
        if self.max_pivot_pair_distance > self.lookback_bars:
            raise ValueError("max_pivot_pair_distance cannot exceed lookback_bars")
        if self.min_pivot_distance > self.max_pivot_pair_distance:
            raise ValueError("min_pivot_distance cannot exceed max_pivot_pair_distance")
        return self


class MTFConfig(BaseModel):
    enabled: bool = True
    base_intervals: list[str] = Field(default_factory=list)
    higher_intervals: list[str] = Field(default_factory=list)
    alignment_method: Literal["asof_backward"] = "asof_backward"
    require_higher_tf_closed: bool = True
    max_alignment_tolerance_bars: int = Field(default=1, ge=0)
    add_higher_tf_prefix: bool = True
    prefix_template: str = "mtf_{interval}_"
    disallow_forward_alignment: bool = True
    disallow_nearest_alignment: bool = True
    drop_unmatched_rows: bool = False
    mark_unmatched_rows: bool = True

    @field_validator("disallow_forward_alignment")
    @classmethod
    def validate_disallow_forward(cls, v: bool) -> bool:
        if not v:
            raise ValueError("disallow_forward_alignment must be True")
        return v

    @field_validator("disallow_nearest_alignment")
    @classmethod
    def validate_disallow_nearest_alignment(cls, v: bool) -> bool:
        if not v:
            raise ValueError("disallow_nearest_alignment must be True")
        return v


class FeatureGroupConfig(BaseModel):
    enabled: bool = True
    groups: dict[str, dict] = Field(default_factory=dict)
    require_group_metadata: bool = True
    allow_ungrouped_features: bool = False


class PatternConfig(BaseModel):
    enabled: bool = True
    native_pattern_skeleton_enabled: bool = True
    talib_pattern_adapter_enabled: bool = True
    fail_if_talib_missing: bool = False
    output_prefix: str = "pat_"
    supported_initial_patterns: list[str] = Field(default_factory=list)
    full_pattern_engine_deferred: bool = True


class IndicatorV2QualityConfig(BaseModel):
    reject_all_nan_feature: bool = True
    reject_inf: bool = True
    warn_high_nan_ratio: bool = True
    max_nan_ratio: float = Field(default=0.50, ge=0.0, le=1.0)
    reject_duplicate_feature_names: bool = True
    reject_unregistered_feature: bool = True
    reject_lookahead_columns: bool = True
    detect_feature_correlation: bool = False
    correlation_warning_threshold: float = Field(default=0.98, ge=0.0, le=1.0)


class IndicatorV2Config(BaseModel):
    enabled: bool = True
    output_dataset_name: str = "indicator_features_v2"
    cache_enabled: bool = True
    cache_dir: str = "data/indicators_v2"
    export_dir: str = "data/indicators_v2/exports"
    prevent_lookahead_bias: bool = True
    require_closed_candles: bool = True
    reject_future_columns: bool = True
    max_feature_columns: int = Field(default=1000, ge=10, le=5000)
    max_feature_groups: int = Field(default=100, ge=1)
    max_mtf_sources_per_run: int = Field(default=5, ge=1)

    pivots: PivotConfig = Field(default_factory=PivotConfig)
    divergence: DivergenceConfig = Field(default_factory=DivergenceConfig)
    mtf: MTFConfig = Field(default_factory=MTFConfig)
    feature_groups: FeatureGroupConfig = Field(default_factory=FeatureGroupConfig)
    patterns: PatternConfig = Field(default_factory=PatternConfig)
    quality: IndicatorV2QualityConfig = Field(default_factory=IndicatorV2QualityConfig)


class StrategyCandidateConfig(BaseModel):
    allowed_directions: list[str] = Field(
        default_factory=lambda: ["bullish", "bearish", "neutral", "no_action"]
    )
    allowed_strengths: list[str] = Field(default_factory=lambda: ["weak", "medium", "strong"])
    min_confidence: float = Field(default=0.0, ge=0.0)
    max_confidence: float = Field(default=100.0, le=100.0)
    default_expiry_bars: int = Field(default=3, ge=1)
    max_expiry_bars: int = Field(default=50, ge=1)
    allow_actionable_order_language: bool = False
    require_non_order_intent: bool = True

    @field_validator("allow_actionable_order_language")
    @classmethod
    def validate_actionable_language(cls, v: bool) -> bool:
        if v:
            raise ValueError("allow_actionable_order_language must be False in Phase 13")
        return v

    @field_validator("require_non_order_intent")
    @classmethod
    def validate_non_order_intent(cls, v: bool) -> bool:
        if not v:
            raise ValueError("require_non_order_intent must be True in Phase 13")
        return v

    @model_validator(mode="after")
    def validate_expiry(self) -> "StrategyCandidateConfig":
        if self.default_expiry_bars > self.max_expiry_bars:
            raise ValueError("default_expiry_bars cannot exceed max_expiry_bars")
        if self.min_confidence > self.max_confidence:
            raise ValueError("min_confidence cannot exceed max_confidence")
        return self


class StrategyPluginConfig(BaseModel):
    enabled: bool = True
    required_features: list[str] = Field(default_factory=list)
    required_prefixes: list[str] = Field(default_factory=list)


class TrendFollowingPluginConfig(StrategyPluginConfig):
    min_adx: float = Field(default=18.0)
    strong_adx: float = Field(default=25.0)
    ema_fast: str = "trend_ema_20"
    ema_mid: str = "trend_ema_50"
    ema_slow: str = "trend_ema_200"


class MeanReversionPluginConfig(StrategyPluginConfig):
    rsi_oversold: float = Field(default=30.0)
    rsi_overbought: float = Field(default=70.0)
    require_bollinger_touch: bool = True


class MomentumContinuationPluginConfig(StrategyPluginConfig):
    rsi_min: float = Field(default=50.0)
    roc_min: float = Field(default=0.0)
    require_macd_hist_positive_for_bullish: bool = True
    require_macd_hist_negative_for_bearish: bool = True


class VolatilityBreakoutPluginConfig(StrategyPluginConfig):
    breakout_buffer_atr: float = Field(default=0.10, ge=0.0)
    require_atr_positive: bool = True


class VolumeConfirmationPluginConfig(StrategyPluginConfig):
    volume_multiplier: float = Field(default=1.25, ge=1.0)
    require_volume_above_average: bool = True


class DivergenceCandidatePluginConfig(StrategyPluginConfig):
    min_divergence_score: float = Field(default=40.0, ge=0.0)
    accept_regular: bool = True
    accept_hidden: bool = True


class MTFConfirmationPluginConfig(StrategyPluginConfig):
    require_mtf_trend_agreement: bool = False
    min_confirming_timeframes: int = Field(default=1, ge=1)


class PatternCandidatePluginConfig(StrategyPluginConfig):
    min_pattern_confidence: float = Field(default=40.0, ge=0.0)


class CompositeSkeletonPluginConfig(StrategyPluginConfig):
    aggregate_only: bool = True
    final_signal_scoring_deferred: bool = True
    min_plugins_agreeing: int = Field(default=2, ge=1)

    @field_validator("final_signal_scoring_deferred")
    @classmethod
    def validate_deferred(cls, v: bool) -> bool:
        if not v:
            raise ValueError("final_signal_scoring_deferred must be True in Phase 13")
        return v


class StrategyPluginsContainerConfig(BaseModel):
    trend_following: TrendFollowingPluginConfig = Field(default_factory=TrendFollowingPluginConfig)
    mean_reversion: MeanReversionPluginConfig = Field(default_factory=MeanReversionPluginConfig)
    momentum_continuation: MomentumContinuationPluginConfig = Field(
        default_factory=MomentumContinuationPluginConfig
    )
    volatility_breakout: VolatilityBreakoutPluginConfig = Field(
        default_factory=VolatilityBreakoutPluginConfig
    )
    volume_confirmation: VolumeConfirmationPluginConfig = Field(
        default_factory=VolumeConfirmationPluginConfig
    )
    divergence_candidate: DivergenceCandidatePluginConfig = Field(
        default_factory=DivergenceCandidatePluginConfig
    )
    mtf_confirmation: MTFConfirmationPluginConfig = Field(
        default_factory=MTFConfirmationPluginConfig
    )
    pattern_candidate: PatternCandidatePluginConfig = Field(
        default_factory=PatternCandidatePluginConfig
    )
    composite_skeleton: CompositeSkeletonPluginConfig = Field(
        default_factory=CompositeSkeletonPluginConfig
    )


class StrategyQualityConfig(BaseModel):
    reject_empty_candidate_set: bool = False
    warn_empty_candidate_set: bool = True
    reject_duplicate_candidates: bool = True
    reject_missing_explanation: bool = True
    reject_order_like_language: bool = True
    reject_confidence_out_of_range: bool = True
    warn_conflicting_candidates: bool = True
    max_conflicting_candidates_per_bar: int = Field(default=5, ge=1)


class StrategiesConfig(BaseModel):
    enabled: bool = True
    output_dataset_name: str = "strategy_candidates"
    cache_enabled: bool = True
    cache_dir: str = "data/strategies"
    export_dir: str = "data/strategies/exports"

    execution_forbidden: bool = True
    order_creation_forbidden: bool = True
    paper_trade_forbidden: bool = True
    backtest_forbidden: bool = True
    live_trade_forbidden: bool = True

    require_explanations: bool = True
    require_feature_metadata: bool = True
    require_closed_candles: bool = True
    prevent_lookahead_bias: bool = True
    reject_future_columns: bool = True
    reject_target_columns: bool = True
    reject_label_columns: bool = True

    max_candidates_per_symbol_interval: int = Field(default=100, ge=1)
    max_plugins_per_run: int = Field(default=20, ge=1, le=100)
    max_conditions_per_plugin: int = Field(default=50, ge=1, le=500)
    min_rows_required: int = Field(default=100, ge=1)
    warmup_rows_allowed: bool = False

    candidate: StrategyCandidateConfig = Field(default_factory=StrategyCandidateConfig)
    plugins: StrategyPluginsContainerConfig = Field(default_factory=StrategyPluginsContainerConfig)
    quality: StrategyQualityConfig = Field(default_factory=StrategyQualityConfig)

    @field_validator(
        "execution_forbidden",
        "order_creation_forbidden",
        "live_trade_forbidden",
        "backtest_forbidden",
        "paper_trade_forbidden",
    )
    @classmethod
    def validate_forbidden(cls, v: bool, info) -> bool:
        if not v:
            raise ValueError(f"{info.field_name} must be True in Phase 13")
        return v


class SignalScoringRulesConfig(BaseModel):
    min_score: float = Field(default=0.0)
    max_score: float = Field(default=100.0)
    default_no_action_score: float = Field(default=0.0)
    confidence_normalization: Literal["linear_0_100"] = Field(default="linear_0_100")
    clamp_scores: bool = Field(default=True)
    round_scores_decimals: int = Field(default=4, ge=0)
    score_tiers: dict[str, tuple[float, float]] = Field(
        default_factory=lambda: {
            "very_low": (0.0, 20.0),
            "low": (20.0, 40.0),
            "medium": (40.0, 60.0),
            "high": (60.0, 80.0),
            "very_high": (80.0, 100.0),
        }
    )
    min_score_for_research_candidate: float = Field(default=50.0)
    min_score_for_risk_review: float = Field(default=65.0)
    min_score_for_future_backtest_candidate: float = Field(default=70.0)

    @model_validator(mode="after")
    def validate_scores(self) -> "SignalScoringRulesConfig":
        if self.min_score >= self.max_score:
            raise ValueError("min_score must be less than max_score")
        return self


class SignalConfluenceConfig(BaseModel):
    enabled: bool = Field(default=True)
    same_direction_bonus_per_plugin: float = Field(default=5.0)
    max_same_direction_bonus: float = Field(default=20.0)
    require_distinct_plugin_types: bool = Field(default=True)
    plugin_type_diversity_bonus: float = Field(default=5.0)
    trend_volume_confirmation_bonus: float = Field(default=5.0)
    mtf_confirmation_bonus: float = Field(default=5.0)
    divergence_confirmation_bonus: float = Field(default=3.0)
    pattern_confirmation_bonus: float = Field(default=1.0)
    max_confluence_score: float = Field(default=100.0)
    min_plugins_for_confluence: int = Field(default=2, ge=1)


class SignalConflictConfig(BaseModel):
    enabled: bool = Field(default=True)
    detect_opposite_direction_same_bar: bool = Field(default=True)
    detect_same_plugin_opposite_direction: bool = Field(default=True)
    bearish_bullish_conflict_penalty: float = Field(default=20.0)
    same_plugin_conflict_penalty: float = Field(default=30.0)
    max_conflict_penalty: float = Field(default=50.0, ge=0.0)
    keep_conflicted_candidates: bool = Field(default=True)
    mark_conflicted_candidates: bool = Field(default=True)


class SignalFreshnessConfig(BaseModel):
    enabled: bool = Field(default=True)
    default_expiry_bars: int = Field(default=3, ge=1)
    max_expiry_bars: int = Field(default=50, ge=1)
    score_decay_mode: Literal["linear", "step"] = Field(default="linear")
    expired_score_multiplier: float = Field(default=0.0, ge=0.0, le=1.0)
    stale_score_multiplier: float = Field(default=0.5, ge=0.0, le=1.0)
    current_bar_multiplier: float = Field(default=1.0, ge=0.0, le=1.0)


class SignalCalibrationConfig(BaseModel):
    enabled: bool = Field(default=True)
    mode: Literal["placeholder_metrics_only"] = Field(default="placeholder_metrics_only")
    require_backtest_before_live_calibration: bool = Field(default=True)
    brier_score_supported: bool = Field(default=True)
    reliability_bins: int = Field(default=10, ge=2, le=50)
    expected_calibration_error_supported: bool = Field(default=True)
    calibration_training_deferred: bool = Field(default=True)

    @field_validator("calibration_training_deferred")
    @classmethod
    def validate_deferred(cls, v: bool) -> bool:
        if not v:
            raise ValueError("calibration_training_deferred must be True in Phase 14")
        return v


class SignalThresholdConfig(BaseModel):
    enabled: bool = Field(default=True)
    no_action_below: float = Field(default=40.0)
    research_candidate_min: float = Field(default=50.0)
    risk_review_min: float = Field(default=65.0)
    future_backtest_candidate_min: float = Field(default=70.0)
    execution_threshold_deferred: bool = Field(default=True)

    @field_validator("execution_threshold_deferred")
    @classmethod
    def validate_deferred(cls, v: bool) -> bool:
        if not v:
            raise ValueError("execution_threshold_deferred must be True in Phase 14")
        return v


class SignalQualityConfig(BaseModel):
    reject_empty_scored_set: bool = Field(default=False)
    warn_empty_scored_set: bool = Field(default=True)
    reject_score_out_of_range: bool = Field(default=True)
    reject_missing_breakdown: bool = Field(default=True)
    reject_missing_explanation: bool = Field(default=True)
    reject_order_language: bool = Field(default=True)
    reject_execution_intent: bool = Field(default=True)
    warn_high_conflict_ratio: bool = Field(default=True)
    max_conflict_ratio: float = Field(default=0.50, ge=0.0, le=1.0)
    warn_single_plugin_high_score: bool = Field(default=True)
    max_single_plugin_score_without_confluence: float = Field(default=70.0)


class SignalsConfig(BaseModel):
    enabled: bool = Field(default=True)
    output_dataset_name: str = Field(default="scored_signal_candidates")
    cache_enabled: bool = Field(default=True)
    cache_dir: str = Field(default="data/signals")
    export_dir: str = Field(default="data/signals/exports")
    execution_forbidden: bool = Field(default=True)
    order_creation_forbidden: bool = Field(default=True)
    paper_trade_forbidden: bool = Field(default=True)
    backtest_forbidden: bool = Field(default=True)
    live_trade_forbidden: bool = Field(default=True)
    risk_engine_required_before_execution: bool = Field(default=True)
    require_explanations: bool = Field(default=True)
    require_score_breakdown: bool = Field(default=True)
    require_candidate_intent_no_order: bool = Field(default=True)
    reject_order_like_language: bool = Field(default=True)
    reject_execution_fields: bool = Field(default=True)
    reject_future_columns: bool = Field(default=True)
    reject_target_columns: bool = Field(default=True)
    reject_label_columns: bool = Field(default=True)
    warmup_candidates_allowed: bool = Field(default=False)

    scoring: SignalScoringRulesConfig = Field(default_factory=SignalScoringRulesConfig)
    plugin_weights: dict[str, float] = Field(
        default_factory=lambda: {
            "trend_following": 1.00,
            "mean_reversion": 0.85,
            "momentum_continuation": 0.90,
            "volatility_breakout": 0.80,
            "volume_confirmation": 0.60,
            "divergence_candidate": 0.75,
            "mtf_confirmation": 0.70,
            "pattern_candidate": 0.35,
            "composite_skeleton": 0.50,
        }
    )
    component_weights: dict[str, float] = Field(
        default_factory=lambda: {
            "candidate_confidence": 0.35,
            "plugin_weighted_score": 0.20,
            "confluence": 0.20,
            "confirmation": 0.10,
            "freshness": 0.05,
            "data_quality": 0.10,
            "conflict_penalty": -0.20,
        }
    )
    confluence: SignalConfluenceConfig = Field(default_factory=SignalConfluenceConfig)
    conflicts: SignalConflictConfig = Field(default_factory=SignalConflictConfig)
    freshness: SignalFreshnessConfig = Field(default_factory=SignalFreshnessConfig)
    calibration: SignalCalibrationConfig = Field(default_factory=SignalCalibrationConfig)
    thresholds: SignalThresholdConfig = Field(default_factory=SignalThresholdConfig)
    quality: SignalQualityConfig = Field(default_factory=SignalQualityConfig)

    @field_validator(
        "execution_forbidden",
        "order_creation_forbidden",
        "live_trade_forbidden",
        "backtest_forbidden",
        "paper_trade_forbidden",
        "risk_engine_required_before_execution",
    )
    @classmethod
    def validate_forbidden(cls, v: bool, info) -> bool:
        if not v:
            raise ValueError(f"{info.field_name} must be True in Phase 14")
        return v

    @field_validator("plugin_weights")
    @classmethod
    def validate_plugin_weights(cls, v: dict[str, float]) -> dict[str, float]:
        for weight in v.values():
            if weight < 0.0 or weight > 5.0:
                raise ValueError("plugin weights must be between 0.0 and 5.0")
        return v


class RegimeClassifierConfig(BaseModel):
    default_method: Literal["rule_based", "gmm_optional", "hmm_optional"] = Field(
        default="rule_based"
    )
    allowed_methods: list[str] = Field(
        default_factory=lambda: ["rule_based", "gmm_optional", "hmm_optional"]
    )
    fail_if_optional_model_missing: bool = Field(default=False)
    rule_based_primary: bool = Field(default=True)
    unsupervised_models_experimental: bool = Field(default=True)
    min_rows_required: int = Field(default=200, ge=50)
    min_valid_feature_ratio: float = Field(default=0.80, ge=0.0, le=1.0)
    max_regime_classes: int = Field(default=10, ge=2)

    @model_validator(mode="after")
    def validate_methods(self) -> "RegimeClassifierConfig":
        if self.default_method not in self.allowed_methods:
            raise ValueError(f"default_method '{self.default_method}' must be in allowed_methods")
        if not self.rule_based_primary:
            raise ValueError("rule_based_primary must be true")
        return self


class RegimeFeatureConfig(BaseModel):
    trend_windows: list[int] = Field(default_factory=lambda: [20, 50, 100, 200])
    volatility_windows: list[int] = Field(default_factory=lambda: [20, 50, 100])
    range_windows: list[int] = Field(default_factory=lambda: [20, 50])
    slope_window: int = Field(default=10)
    return_windows: list[int] = Field(default_factory=lambda: [2, 5, 10, 20])
    atr_period: int = Field(default=14)
    adx_period: int = Field(default=14)
    bb_width_period: int = Field(default=20)
    realized_vol_period: int = Field(default=20)
    volume_window: int = Field(default=20)
    use_indicator_features: bool = Field(default=True)
    use_signal_features: bool = Field(default=True)
    use_mtf_features: bool = Field(default=True)

    @model_validator(mode="after")
    def validate_windows(self) -> "RegimeFeatureConfig":
        all_windows = (
            self.trend_windows
            + self.volatility_windows
            + self.range_windows
            + self.return_windows
            + [
                self.slope_window,
                self.atr_period,
                self.adx_period,
                self.bb_width_period,
                self.realized_vol_period,
                self.volume_window,
            ]
        )
        if any(w <= 1 for w in all_windows):
            raise ValueError("All window sizes must be > 1")
        return self


class RegimeThresholdConfig(BaseModel):
    trend_adx_min: float = Field(default=20.0)
    strong_trend_adx_min: float = Field(default=25.0)
    trend_slope_min_abs: float = Field(default=0.0005)
    range_adx_max: float = Field(default=18.0)
    range_bb_width_max_pct: float = Field(default=4.0)
    volatile_realized_vol_z_min: float = Field(default=1.0)
    volatile_atr_z_min: float = Field(default=1.0)
    calm_realized_vol_z_max: float = Field(default=-0.5)
    calm_atr_z_max: float = Field(default=-0.5)
    transition_confidence_max: float = Field(default=55.0)
    min_regime_confidence: float = Field(default=0.0, ge=0.0)
    max_regime_confidence: float = Field(default=100.0, le=100.0)

    @model_validator(mode="after")
    def validate_thresholds(self) -> "RegimeThresholdConfig":
        if self.strong_trend_adx_min < self.trend_adx_min:
            raise ValueError("strong_trend_adx_min must be >= trend_adx_min")
        if self.range_adx_max >= self.strong_trend_adx_min:
            raise ValueError("range_adx_max must be < strong_trend_adx_min")
        return self


class RegimeSmoothingConfig(BaseModel):
    enabled: bool = Field(default=True)
    min_regime_duration_bars: int = Field(default=3)
    transition_buffer_bars: int = Field(default=2)
    majority_vote_window: int = Field(default=5)
    allow_single_bar_flip: bool = Field(default=False)
    unknown_for_unstable_flips: bool = Field(default=True)


class RegimeTransitionConfig(BaseModel):
    enabled: bool = Field(default=True)
    detect_regime_changes: bool = Field(default=True)
    mark_transition_bars: bool = Field(default=True)
    transition_lookback_bars: int = Field(default=5)
    max_transition_events_per_1000_bars: int = Field(default=300)


class RegimeStabilityConfig(BaseModel):
    enabled: bool = Field(default=True)
    stability_window: int = Field(default=20)
    min_stability_score: float = Field(default=0.0)
    max_stability_score: float = Field(default=100.0)
    penalize_frequent_flips: bool = Field(default=True)
    flip_penalty_per_event: float = Field(default=5.0)


class RegimeOptionalGMMConfig(BaseModel):
    enabled: bool = Field(default=False)
    n_components: int = Field(default=5)
    covariance_type: str = Field(default="diag")
    random_state: int = Field(default=42)
    max_iter: int = Field(default=200)
    require_train_split: bool = Field(default=True)
    scaler: str = Field(default="standard")

    @model_validator(mode="after")
    def validate_gmm(self) -> "RegimeOptionalGMMConfig":
        if self.enabled and not self.require_train_split:
            raise ValueError("require_train_split must be True when GMM is enabled")
        return self


class RegimeOptionalHMMConfig(BaseModel):
    enabled: bool = Field(default=False)
    n_components: int = Field(default=5)
    covariance_type: str = Field(default="diag")
    random_state: int = Field(default=42)
    max_iter: int = Field(default=200)
    require_train_split: bool = Field(default=True)
    installed_optional: bool = Field(default=False)

    @model_validator(mode="after")
    def validate_hmm(self) -> "RegimeOptionalHMMConfig":
        if self.enabled and not self.require_train_split:
            raise ValueError("require_train_split must be True when HMM is enabled")
        return self


class RegimeQualityConfig(BaseModel):
    reject_all_unknown: bool = Field(default=False)
    warn_all_unknown: bool = Field(default=True)
    reject_missing_explanation: bool = Field(default=True)
    reject_confidence_out_of_range: bool = Field(default=True)
    warn_high_transition_ratio: bool = Field(default=True)
    max_transition_ratio: float = Field(default=0.30, ge=0.0, le=1.0)
    reject_lookahead_risk: bool = Field(default=True)
    reject_unclosed_candle_usage: bool = Field(default=True)
    reject_model_fit_on_full_dataset: bool = Field(default=True)


class RegimesConfig(BaseModel):
    enabled: bool = Field(default=True)
    output_dataset_name: str = Field(default="market_regimes")
    cache_enabled: bool = Field(default=True)
    cache_dir: str = Field(default="data/regimes")
    export_dir: str = Field(default="data/regimes/exports")
    execution_forbidden: bool = Field(default=True)
    order_creation_forbidden: bool = Field(default=True)
    paper_trade_forbidden: bool = Field(default=True)
    backtest_forbidden: bool = Field(default=True)
    live_trade_forbidden: bool = Field(default=True)
    require_closed_candles: bool = Field(default=True)
    prevent_lookahead_bias: bool = Field(default=True)
    reject_future_columns: bool = Field(default=True)
    reject_target_columns: bool = Field(default=True)
    reject_label_columns: bool = Field(default=True)
    reject_execution_columns: bool = Field(default=True)
    warmup_rows_allowed: bool = Field(default=False)

    classifier: RegimeClassifierConfig = Field(default_factory=RegimeClassifierConfig)
    features: RegimeFeatureConfig = Field(default_factory=RegimeFeatureConfig)
    thresholds: RegimeThresholdConfig = Field(default_factory=RegimeThresholdConfig)
    smoothing: RegimeSmoothingConfig = Field(default_factory=RegimeSmoothingConfig)
    transitions: RegimeTransitionConfig = Field(default_factory=RegimeTransitionConfig)
    stability: RegimeStabilityConfig = Field(default_factory=RegimeStabilityConfig)
    optional_models: dict = Field(
        default_factory=lambda: {"gmm": RegimeOptionalGMMConfig(), "hmm": RegimeOptionalHMMConfig()}
    )
    quality: RegimeQualityConfig = Field(default_factory=RegimeQualityConfig)

    @model_validator(mode="after")
    def validate_forbidden(self) -> "RegimesConfig":
        if not self.execution_forbidden:
            raise ValueError("execution_forbidden must be True")
        if not self.order_creation_forbidden:
            raise ValueError("order_creation_forbidden must be True")
        if not self.paper_trade_forbidden:
            raise ValueError("paper_trade_forbidden must be True")
        if not self.backtest_forbidden:
            raise ValueError("backtest_forbidden must be True")
        if not self.live_trade_forbidden:
            raise ValueError("live_trade_forbidden must be True")
        return self


class RiskAccountConfig(BaseModel):
    account_equity_source: str = "simulated_config_only"
    simulated_account_equity_usdt: float = Field(1000.0, gt=0)
    allow_real_balance_fetch: bool = False
    allow_account_api: bool = False
    equity_currency: str = "USDT"

    @model_validator(mode="after")
    def validate_safety(self) -> "RiskAccountConfig":
        if self.allow_real_balance_fetch:
            raise ValueError("allow_real_balance_fetch must be False in this phase")
        if self.allow_account_api:
            raise ValueError("allow_account_api must be False in this phase")
        return self


class RiskGlobalLimitsConfig(BaseModel):
    max_total_risk_pct: float = Field(2.0, ge=0)
    max_daily_loss_pct: float = Field(1.0, ge=0)
    max_weekly_loss_pct: float = Field(3.0, ge=0)
    max_monthly_loss_pct: float = Field(6.0, ge=0)
    max_open_risk_candidates: int = Field(5, ge=1)
    max_correlated_candidates: int = Field(3, ge=1)
    max_symbols_with_risk: int = Field(5, ge=1)
    max_candidates_per_hour: int = Field(20, ge=1)
    max_candidates_per_day: int = Field(100, ge=1)
    min_signal_score_for_risk_review: float = Field(65.0, ge=0, le=100)
    min_signal_score_for_future_backtest: float = Field(70.0, ge=0, le=100)
    min_signal_score_for_paper_review: float = Field(75.0, ge=0, le=100)


class RiskPositionConfig(BaseModel):
    enabled: bool = True
    mode: str = "hypothetical_only"
    max_position_risk_pct: float = Field(0.25, ge=0, le=5)
    max_symbol_exposure_pct: float = Field(10.0, ge=0, le=100)
    max_total_exposure_pct: float = Field(30.0, ge=0, le=100)
    min_notional_usdt: float = Field(10.0, ge=0)
    max_notional_per_candidate_usdt: float = Field(100.0, ge=0)
    allow_fractional_quantity_estimate: bool = True
    round_to_lot_size_for_estimate: bool = True
    produce_order_quantity: bool = False
    produce_entry_price: bool = False
    produce_exit_price: bool = False
    produce_stop_loss: bool = False
    produce_take_profit: bool = False

    @model_validator(mode="after")
    def validate_safety(self) -> "RiskPositionConfig":
        if self.produce_order_quantity:
            raise ValueError("produce_order_quantity must be False in this phase")
        if self.produce_entry_price:
            raise ValueError("produce_entry_price must be False in this phase")
        if self.produce_exit_price:
            raise ValueError("produce_exit_price must be False in this phase")
        if self.produce_stop_loss:
            raise ValueError("produce_stop_loss must be False in this phase")
        if self.produce_take_profit:
            raise ValueError("produce_take_profit must be False in this phase")
        return self


class RiskSpotConfig(BaseModel):
    enabled: bool = True
    allow_short: bool = False
    allow_margin: bool = False
    require_symbol_filters: bool = True
    require_min_notional_check: bool = True
    require_lot_size_check: bool = True
    require_price_filter_check: bool = True
    reject_if_filter_metadata_missing: bool = True


class RiskFuturesConfig(BaseModel):
    enabled: bool = True
    allow_usdm_futures_context: bool = True
    allow_live_leverage_change: bool = False
    allow_margin_mode_change: bool = False
    allow_position_mode_change: bool = False
    default_leverage_for_estimate: int = Field(1, ge=1)
    max_leverage_for_estimate: int = Field(3, ge=1)
    hard_max_leverage_allowed: int = Field(5, ge=1, le=10)
    reject_if_leverage_above_policy: bool = True
    liquidation_model_deferred: bool = True
    maintenance_margin_model_deferred: bool = True
    require_position_risk_snapshot_for_future_execution: bool = True

    @model_validator(mode="after")
    def validate_leverage(self) -> "RiskFuturesConfig":
        if self.max_leverage_for_estimate > self.hard_max_leverage_allowed:
            raise ValueError("max_leverage_for_estimate cannot exceed hard_max_leverage_allowed")
        if self.allow_live_leverage_change:
            raise ValueError("allow_live_leverage_change must be False in this phase")
        return self


class RiskVolatilityConfig(BaseModel):
    enabled: bool = True
    max_atr_pct_for_candidate: float = Field(8.0, ge=0)
    max_realized_vol_z: float = Field(3.0, ge=0)
    high_volatility_penalty: float = Field(20.0, ge=0)
    volatile_regime_penalty: float = Field(15.0, ge=0)
    calm_regime_bonus: float = Field(5.0, ge=0)
    reject_extreme_volatility: bool = True


class RiskLiquidityConfig(BaseModel):
    enabled: bool = True
    max_spread_bps: float = Field(10.0, ge=0)
    warning_spread_bps: float = Field(6.0, ge=0)
    min_quote_volume_24h_usdt: float = Field(10000000.0, ge=0)
    min_book_depth_notional_usdt: float = Field(1000.0, ge=0)
    high_spread_penalty: float = Field(15.0, ge=0)
    low_liquidity_penalty: float = Field(20.0, ge=0)
    reject_missing_liquidity_metadata: bool = True


class RiskRegimeConfig(BaseModel):
    enabled: bool = True
    use_regime_context: bool = True
    reject_unknown_regime: bool = False
    unknown_regime_penalty: float = Field(10.0, ge=0)
    transition_regime_penalty: float = Field(10.0, ge=0)
    volatile_regime_penalty: float = Field(15.0, ge=0)
    range_trend_mismatch_penalty: float = Field(10.0, ge=0)
    trend_following_requires_trend_regime: bool = False
    mean_reversion_prefers_range_regime: bool = False


class RiskConflictConfig(BaseModel):
    enabled: bool = True
    reject_high_conflict: bool = False
    high_conflict_penalty: float = Field(20.0, ge=0)
    max_conflict_ratio_allowed: float = Field(0.50, ge=0, le=1)
    reject_same_plugin_opposite_direction: bool = True


class RiskDataQualityConfig(BaseModel):
    enabled: bool = True
    reject_missing_score_breakdown: bool = True
    reject_missing_regime_context: bool = False
    reject_low_data_quality: bool = True
    max_quality_issue_severity_allowed: str = "warning"
    data_quality_penalty: float = Field(20.0, ge=0)


class RiskFrequencyConfig(BaseModel):
    enabled: bool = True
    order_rate_model_only: bool = True
    max_risk_reviews_per_symbol_per_hour: int = Field(10, ge=1)
    max_risk_reviews_total_per_hour: int = Field(50, ge=1)
    max_same_direction_candidates_per_symbol_per_hour: int = Field(5, ge=1)
    cooldown_after_rejection_bars: int = Field(3, ge=0)


class RiskDecisionConfig(BaseModel):
    min_final_risk_score: float = Field(60.0, ge=0, le=100)
    approved_for_future_backtest_min_score: float = Field(65.0, ge=0, le=100)
    approved_for_paper_review_min_score: float = Field(75.0, ge=0, le=100)
    needs_review_min_score: float = Field(50.0, ge=0, le=100)
    reject_below_score: float = Field(40.0, ge=0, le=100)
    max_risk_score: float = Field(100.0, ge=0, le=100)
    score_clamp: bool = True
    require_explanation: bool = True
    require_breakdown: bool = True
    allow_only_non_execution_intents: bool = True

    @model_validator(mode="after")
    def validate_thresholds(self) -> "RiskDecisionConfig":
        if not (
            self.reject_below_score
            <= self.needs_review_min_score
            <= self.min_final_risk_score
            <= self.approved_for_future_backtest_min_score
            <= self.approved_for_paper_review_min_score
            <= self.max_risk_score
        ):
            raise ValueError("Decision thresholds must be ordered")
        return self


class RiskQualityConfig(BaseModel):
    reject_missing_explanation: bool = True
    reject_missing_breakdown: bool = True
    reject_score_out_of_range: bool = True
    reject_execution_fields: bool = True
    reject_order_like_language: bool = True
    warn_empty_assessment_set: bool = True
    reject_empty_assessment_set: bool = False


class RiskConfig(BaseModel):
    enabled: bool = True
    output_dataset_name: str = "risk_assessments"
    cache_enabled: bool = True
    cache_dir: str = "data/risk"
    export_dir: str = "data/risk/exports"

    execution_forbidden: bool = True
    order_creation_forbidden: bool = True
    paper_trade_forbidden: bool = True
    backtest_forbidden: bool = True
    live_trade_forbidden: bool = True
    require_execution_layer_before_orders: bool = True
    require_backtest_before_paper: bool = True
    require_paper_before_live: bool = True

    account: RiskAccountConfig = Field(default_factory=RiskAccountConfig)
    global_limits: RiskGlobalLimitsConfig = Field(default_factory=RiskGlobalLimitsConfig)
    position_risk: RiskPositionConfig = Field(default_factory=RiskPositionConfig)
    spot: RiskSpotConfig = Field(default_factory=RiskSpotConfig)
    futures: RiskFuturesConfig = Field(default_factory=RiskFuturesConfig)
    volatility: RiskVolatilityConfig = Field(default_factory=RiskVolatilityConfig)
    liquidity: RiskLiquidityConfig = Field(default_factory=RiskLiquidityConfig)
    regime: RiskRegimeConfig = Field(default_factory=RiskRegimeConfig)
    conflicts: RiskConflictConfig = Field(default_factory=RiskConflictConfig)
    data_quality: RiskDataQualityConfig = Field(default_factory=RiskDataQualityConfig)
    frequency: RiskFrequencyConfig = Field(default_factory=RiskFrequencyConfig)
    decision: RiskDecisionConfig = Field(default_factory=RiskDecisionConfig)
    quality: RiskQualityConfig = Field(default_factory=RiskQualityConfig)

    @model_validator(mode="after")
    def validate_safety(self) -> "RiskConfig":
        if not self.execution_forbidden:
            raise ValueError("execution_forbidden must be True")
        if not self.order_creation_forbidden:
            raise ValueError("order_creation_forbidden must be True")
        if not self.live_trade_forbidden:
            raise ValueError("live_trade_forbidden must be True")
        if not self.paper_trade_forbidden:
            raise ValueError("paper_trade_forbidden must be True")
        if not self.backtest_forbidden:
            raise ValueError("backtest_forbidden must be True")
        return self


class PaperAccountConfig(BaseModel):
    mode: str = "local_simulated"
    starting_cash_usdt: float = Field(1000.0, gt=0)
    quote_currency: str = "USDT"
    allow_negative_cash: bool = False
    allow_margin: bool = False
    allow_short_spot: bool = False
    allow_futures_simulation: bool = True
    futures_leverage_simulation_only: bool = True
    default_futures_leverage_estimate: int = Field(1, ge=1)
    max_futures_leverage_estimate: int = Field(3, ge=1, le=5)

    @model_validator(mode="after")
    def validate_account(self) -> "PaperAccountConfig":
        if self.allow_negative_cash:
            raise ValueError("allow_negative_cash must be False in paper mode")
        if self.allow_margin:
            raise ValueError("allow_margin must be False in paper mode")
        if self.allow_short_spot:
            raise ValueError("allow_short_spot must be False in paper mode")
        if self.default_futures_leverage_estimate > self.max_futures_leverage_estimate:
            raise ValueError(
                "default_futures_leverage_estimate cannot exceed max_futures_leverage_estimate"
            )
        return self


class PaperCandidateAcceptanceConfig(BaseModel):
    require_risk_assessment: bool = True
    allowed_risk_statuses: list[str] = ["approved_for_future_backtest", "approved_for_paper_review"]
    min_final_risk_score: float = Field(65.0, ge=0, le=100)
    min_signal_score: float = Field(65.0, ge=0, le=100)
    reject_needs_review_by_default: bool = True
    reject_blocked_or_rejected: bool = True
    require_no_order_intent: bool = True
    require_no_execution_fields: bool = True


class PaperSimulationConfig(BaseModel):
    mode: str = "sequential_bar"
    fill_model: str = "next_bar_open"
    allow_same_bar_fill: bool = False
    require_next_candle: bool = True
    max_open_positions: int = Field(3, ge=1)
    max_positions_per_symbol: int = Field(1, ge=1)
    max_new_positions_per_bar: int = Field(2, ge=1)
    max_new_positions_per_day: int = Field(20, ge=1)
    close_on_opposite_candidate: bool = True
    close_on_expired_candidate: bool = False
    allow_partial_fill: bool = False
    mark_to_market: bool = True


class PaperSizingConfig(BaseModel):
    mode: str = "fixed_fractional_notional"
    fixed_notional_usdt: float = Field(50.0, gt=0)
    max_notional_usdt: float = Field(100.0, gt=0)
    max_cash_usage_pct: float = Field(30.0, ge=0, le=100)
    risk_assessment_notional_cap_required: bool = True
    use_risk_hypothetical_notional_cap: bool = True
    produce_real_order_quantity: bool = False
    quantity_is_simulated_only: bool = True

    @model_validator(mode="after")
    def validate_sizing(self) -> "PaperSizingConfig":
        if self.produce_real_order_quantity:
            raise ValueError("produce_real_order_quantity must be False in paper mode")
        if not self.quantity_is_simulated_only:
            raise ValueError("quantity_is_simulated_only must be True in paper mode")
        if self.max_notional_usdt < self.fixed_notional_usdt:
            raise ValueError("max_notional_usdt must be >= fixed_notional_usdt")
        return self


class PaperFeeConfig(BaseModel):
    enabled: bool = True
    maker_fee_bps: float = Field(10.0, ge=0)
    taker_fee_bps: float = Field(10.0, ge=0)
    default_fee_side: str = "taker"
    fee_currency: str = "USDT"
    futures_fee_model_deferred: bool = True


class PaperSlippageConfig(BaseModel):
    enabled: bool = True
    model: str = "bps"
    default_slippage_bps: float = Field(2.0, ge=0)
    max_slippage_bps: float = Field(20.0, ge=0)
    volatility_slippage_multiplier: float = Field(1.5, ge=0)
    spread_slippage_multiplier: float = Field(1.0, ge=0)


class PaperPnLConfig(BaseModel):
    enabled: bool = True
    realized_pnl_enabled: bool = True
    unrealized_pnl_enabled: bool = True
    mark_price_source: str = "close"
    use_last_close_for_mark: bool = True
    include_fees: bool = True
    include_slippage: bool = True


class PaperSafetyConfig(BaseModel):
    reject_if_real_exchange_enabled: bool = True
    reject_if_order_gateway_enabled: bool = True
    reject_if_api_credentials_present_for_paper: bool = False
    reject_execution_fields: bool = True
    reject_order_like_language: bool = True
    reject_unknown_fill_model: bool = True
    reject_negative_cash: bool = True
    reject_position_without_ledger_event: bool = True
    reject_unmatched_close: bool = True


class PaperQualityConfig(BaseModel):
    reject_missing_ledger_event: bool = True
    reject_invalid_cash_balance: bool = True
    reject_invalid_position_state: bool = True
    reject_missing_fill_price: bool = True
    reject_missing_fee: bool = True
    warn_empty_paper_run: bool = True
    reject_empty_paper_run: bool = False


class PaperConfig(BaseModel):
    enabled: bool = True
    output_dataset_name: str = "paper_trades"
    cache_enabled: bool = True
    cache_dir: str = "data/paper"
    export_dir: str = "data/paper/exports"
    ledger_dir: str = "data/paper/ledger"
    journal_dir: str = "data/paper/journal"

    real_exchange_forbidden: bool = True
    binance_client_forbidden: bool = True
    order_gateway_forbidden: bool = True
    testnet_order_forbidden: bool = True
    live_order_forbidden: bool = True
    signed_request_forbidden: bool = True
    api_key_forbidden: bool = True

    account: PaperAccountConfig = Field(default_factory=PaperAccountConfig)
    candidate_acceptance: PaperCandidateAcceptanceConfig = Field(
        default_factory=PaperCandidateAcceptanceConfig
    )
    simulation: PaperSimulationConfig = Field(default_factory=PaperSimulationConfig)
    sizing: PaperSizingConfig = Field(default_factory=PaperSizingConfig)
    fees: PaperFeeConfig = Field(default_factory=PaperFeeConfig)
    slippage: PaperSlippageConfig = Field(default_factory=PaperSlippageConfig)
    pnl: PaperPnLConfig = Field(default_factory=PaperPnLConfig)
    safety: PaperSafetyConfig = Field(default_factory=PaperSafetyConfig)
    quality: PaperQualityConfig = Field(default_factory=PaperQualityConfig)

    @model_validator(mode="after")
    def validate_paper_safety(self) -> "PaperConfig":
        if not self.real_exchange_forbidden:
            raise ValueError("real_exchange_forbidden must be True in paper mode")
        if not self.binance_client_forbidden:
            raise ValueError("binance_client_forbidden must be True in paper mode")
        if not self.order_gateway_forbidden:
            raise ValueError("order_gateway_forbidden must be True in paper mode")
        if not self.testnet_order_forbidden:
            raise ValueError("testnet_order_forbidden must be True in paper mode")
        if not self.live_order_forbidden:
            raise ValueError("live_order_forbidden must be True in paper mode")
        if not self.signed_request_forbidden:
            raise ValueError("signed_request_forbidden must be True in paper mode")
        if not self.api_key_forbidden:
            raise ValueError("api_key_forbidden must be True in paper mode")
        return self


class BacktestModeConfig(BaseModel):
    engine: str = Field("event_driven", description="Engine mode")
    deterministic: bool = Field(True, description="Deterministic run")
    random_seed: int = Field(42, description="Random seed")
    allow_randomness: bool = Field(False, description="Allow randomness")
    single_symbol_default: bool = Field(True, description="Single symbol default")
    multi_symbol_enabled: bool = Field(True, description="Multi symbol enabled")
    portfolio_backtest_enabled: bool = Field(False, description="Portfolio backtest enabled")


class BacktestDataConfig(BaseModel):
    source_priority: list[str] = Field(
        ["warehouse", "market_data_cache", "fixture"], description="Source priority"
    )
    require_ohlcv_quality_passed: bool = Field(True, description="Require quality passed")
    reject_duplicate_open_time: bool = Field(True, description="Reject duplicate open time")
    reject_gaps: bool = Field(False, description="Reject gaps")
    warn_gaps: bool = Field(True, description="Warn gaps")
    reject_out_of_order: bool = Field(True, description="Reject out of order")
    reject_incomplete_last_candle: bool = Field(True, description="Reject incomplete last candle")
    min_rows_required: int = Field(300, description="Min rows required")
    warmup_rows_for_indicators: int = Field(250, description="Warmup rows for indicators")
    trade_after_warmup_only: bool = Field(True, description="Trade after warmup only")
    require_closed_candles: bool = Field(True, description="Require closed candles")


class BacktestTimingConfig(BaseModel):
    decision_price_source: str = Field("close", description="Decision price source")
    fill_model: str = Field("next_bar_open", description="Fill model")
    allow_same_bar_fill: bool = Field(False, description="Allow same bar fill")
    require_next_candle_for_fill: bool = Field(True, description="Require next candle for fill")
    decision_on_closed_candle_only: bool = Field(True, description="Decision on closed candle only")
    fill_on_future_candle_only: bool = Field(True, description="Fill on future candle only")
    max_signal_age_bars: int = Field(3, description="Max signal age bars")
    expire_signal_if_not_filled: bool = Field(True, description="Expire signal if not filled")


class BacktestCapitalConfig(BaseModel):
    starting_cash_usdt: float = Field(1000.0, description="Starting cash USDT", gt=0)
    quote_currency: str = Field("USDT", description="Quote currency")
    allow_negative_cash: bool = Field(False, description="Allow negative cash")
    allow_margin: bool = Field(False, description="Allow margin")
    allow_short_spot: bool = Field(False, description="Allow short spot")
    max_cash_usage_pct: float = Field(30.0, description="Max cash usage pct", ge=0, le=100)
    max_open_positions: int = Field(3, description="Max open positions", ge=1)
    max_positions_per_symbol: int = Field(1, description="Max positions per symbol")


class BacktestSizingConfig(BaseModel):
    mode: str = Field("fixed_notional", description="Sizing mode")
    fixed_notional_usdt: float = Field(50.0, description="Fixed notional USDT", gt=0)
    max_notional_usdt: float = Field(100.0, description="Max notional USDT")
    use_risk_notional_cap: bool = Field(True, description="Use risk notional cap")
    risk_cap_required: bool = Field(True, description="Risk cap required")
    quantity_is_simulated_only: bool = Field(True, description="Quantity is simulated only")
    produce_real_order_quantity: bool = Field(False, description="Produce real order quantity")


class BacktestFeeConfig(BaseModel):
    enabled: bool = Field(True, description="Enabled")
    maker_fee_bps: float = Field(10.0, description="Maker fee bps")
    taker_fee_bps: float = Field(10.0, description="Taker fee bps")
    default_fee_side: str = Field("taker", description="Default fee side")
    include_fees_in_pnl: bool = Field(True, description="Include fees in pnl")


class BacktestSlippageConfig(BaseModel):
    enabled: bool = Field(True, description="Enabled")
    model: str = Field("bps", description="Model")
    default_slippage_bps: float = Field(2.0, description="Default slippage bps")
    max_slippage_bps: float = Field(20.0, description="Max slippage bps")
    volatility_slippage_multiplier: float = Field(1.5, description="Volatility slippage multiplier")
    spread_slippage_multiplier: float = Field(1.0, description="Spread slippage multiplier")
    include_slippage_in_pnl: bool = Field(True, description="Include slippage in pnl")


class BacktestExitConfig(BaseModel):
    enabled: bool = Field(True, description="Enabled")
    close_on_opposite_signal: bool = Field(True, description="Close on opposite signal")
    close_on_signal_expiry: bool = Field(False, description="Close on signal expiry")
    close_on_end_of_backtest: bool = Field(True, description="Close on end of backtest")
    max_holding_bars_enabled: bool = Field(True, description="Max holding bars enabled")
    max_holding_bars: int = Field(100, description="Max holding bars", gt=0)
    stop_loss_deferred: bool = Field(True, description="Stop loss deferred")
    take_profit_deferred: bool = Field(True, description="Take profit deferred")
    trailing_stop_deferred: bool = Field(True, description="Trailing stop deferred")


class BacktestMetricsConfig(BaseModel):
    enabled: bool = Field(True, description="Enabled")
    compute_equity_curve: bool = Field(True, description="Compute equity curve")
    compute_drawdown: bool = Field(True, description="Compute drawdown")
    compute_win_rate: bool = Field(True, description="Compute win rate")
    compute_profit_factor: bool = Field(True, description="Compute profit factor")
    compute_expectancy: bool = Field(True, description="Compute expectancy")
    compute_avg_trade: bool = Field(True, description="Compute avg trade")
    compute_exposure_time: bool = Field(True, description="Compute exposure time")
    compute_turnover: bool = Field(True, description="Compute turnover")
    compute_fee_impact: bool = Field(True, description="Compute fee impact")
    compute_slippage_impact: bool = Field(True, description="Compute slippage impact")
    compute_benchmark_placeholder: bool = Field(True, description="Compute benchmark placeholder")
    risk_free_rate_annual: float = Field(0.0, description="Risk free rate annual")


class BacktestBenchmarkConfig(BaseModel):
    enabled: bool = Field(True, description="Enabled")
    method: str = Field("buy_and_hold_placeholder", description="Method")
    same_period: bool = Field(True, description="Same period")
    include_fees: bool = Field(False, description="Include fees")
    include_slippage: bool = Field(False, description="Include slippage")
    benchmark_symbol_same_as_test: bool = Field(True, description="Benchmark symbol same as test")


class BacktestLeakageConfig(BaseModel):
    prevent_lookahead_bias: bool = Field(True, description="Prevent lookahead bias")
    reject_future_columns: bool = Field(True, description="Reject future columns")
    reject_target_columns: bool = Field(True, description="Reject target columns")
    reject_label_columns: bool = Field(True, description="Reject label columns")
    reject_forward_alignment: bool = Field(True, description="Reject forward alignment")
    reject_nearest_alignment: bool = Field(True, description="Reject nearest alignment")
    require_backward_asof_alignment: bool = Field(
        True, description="Require backward asof alignment"
    )
    reject_centered_rolling: bool = Field(True, description="Reject centered rolling")
    reject_same_bar_fill: bool = Field(True, description="Reject same bar fill")
    reject_unclosed_candle_decision: bool = Field(
        True, description="Reject unclosed candle decision"
    )


class BacktestQualityConfig(BaseModel):
    reject_empty_backtest: bool = Field(False, description="Reject empty backtest")
    warn_empty_backtest: bool = Field(True, description="Warn empty backtest")
    reject_missing_trade_explanation: bool = Field(
        True, description="Reject missing trade explanation"
    )
    reject_invalid_equity_curve: bool = Field(True, description="Reject invalid equity curve")
    reject_negative_cash: bool = Field(True, description="Reject negative cash")
    reject_unmatched_position_close: bool = Field(
        True, description="Reject unmatched position close"
    )
    reject_position_without_fill: bool = Field(True, description="Reject position without fill")
    reject_fill_without_event: bool = Field(True, description="Reject fill without event")
    reject_metric_nan_inf: bool = Field(True, description="Reject metric nan inf")
    warn_low_trade_count: bool = Field(True, description="Warn low trade count")
    min_trade_count_warning: int = Field(5, description="Min trade count warning")


class BacktestConfig(BaseModel):
    enabled: bool = Field(True, description="Enabled")
    output_dataset_name: str = Field("backtest_runs", description="Output dataset name")
    cache_enabled: bool = Field(True, description="Cache enabled")
    cache_dir: str = Field("data/backtest", description="Cache dir")
    export_dir: str = Field("data/backtest/exports", description="Export dir")
    reports_dir: str = Field("data/backtest/reports", description="Reports dir")

    real_exchange_forbidden: bool = Field(True, description="Real exchange forbidden")
    binance_client_forbidden: bool = Field(True, description="Binance client forbidden")
    order_gateway_forbidden: bool = Field(True, description="Order gateway forbidden")
    testnet_order_forbidden: bool = Field(True, description="Testnet order forbidden")
    live_order_forbidden: bool = Field(True, description="Live order forbidden")
    signed_request_forbidden: bool = Field(True, description="Signed request forbidden")
    api_key_forbidden: bool = Field(True, description="API key forbidden")

    mode: BacktestModeConfig = Field(default_factory=BacktestModeConfig)
    data: BacktestDataConfig = Field(default_factory=BacktestDataConfig)
    timing: BacktestTimingConfig = Field(default_factory=BacktestTimingConfig)
    capital: BacktestCapitalConfig = Field(default_factory=BacktestCapitalConfig)
    sizing: BacktestSizingConfig = Field(default_factory=BacktestSizingConfig)
    fees: BacktestFeeConfig = Field(default_factory=BacktestFeeConfig)
    slippage: BacktestSlippageConfig = Field(default_factory=BacktestSlippageConfig)
    exits: BacktestExitConfig = Field(default_factory=BacktestExitConfig)
    metrics: BacktestMetricsConfig = Field(default_factory=BacktestMetricsConfig)
    benchmark: BacktestBenchmarkConfig = Field(default_factory=BacktestBenchmarkConfig)
    leakage: BacktestLeakageConfig = Field(default_factory=BacktestLeakageConfig)
    quality: BacktestQualityConfig = Field(default_factory=BacktestQualityConfig)

    @model_validator(mode="after")
    def validate_backtest_config(self) -> "BacktestConfig":
        if not self.real_exchange_forbidden:
            raise ValueError("real_exchange_forbidden must be True in Phase 18")
        if not self.binance_client_forbidden:
            raise ValueError("binance_client_forbidden must be True in Phase 18")
        if not self.order_gateway_forbidden:
            raise ValueError("order_gateway_forbidden must be True in Phase 18")
        if not self.testnet_order_forbidden:
            raise ValueError("testnet_order_forbidden must be True in Phase 18")
        if not self.live_order_forbidden:
            raise ValueError("live_order_forbidden must be True in Phase 18")
        if not self.signed_request_forbidden:
            raise ValueError("signed_request_forbidden must be True in Phase 18")
        if not self.api_key_forbidden:
            raise ValueError("api_key_forbidden must be True in Phase 18")
        if not self.mode.deterministic:
            raise ValueError("deterministic must be True")
        if self.mode.allow_randomness:
            raise ValueError("allow_randomness must be False")
        if self.timing.allow_same_bar_fill:
            raise ValueError("allow_same_bar_fill must be False")
        if not self.timing.fill_on_future_candle_only:
            raise ValueError("fill_on_future_candle_only must be True")
        if not self.timing.decision_on_closed_candle_only:
            raise ValueError("decision_on_closed_candle_only must be True")
        if not self.leakage.reject_same_bar_fill:
            raise ValueError("reject_same_bar_fill must be True")
        if not self.leakage.reject_centered_rolling:
            raise ValueError("reject_centered_rolling must be True")
        if self.sizing.max_notional_usdt < self.sizing.fixed_notional_usdt:
            raise ValueError("max_notional_usdt must be >= fixed_notional_usdt")
        if not self.exits.stop_loss_deferred:
            raise ValueError("stop_loss_deferred must be True")
        if not self.exits.take_profit_deferred:
            raise ValueError("take_profit_deferred must be True")
        if not self.exits.trailing_stop_deferred:
            raise ValueError("trailing_stop_deferred must be True")
        if self.sizing.produce_real_order_quantity:
            raise ValueError("produce_real_order_quantity must be False")
        return self


class BacktestReportingMetricsConfig(BaseModel):
    enabled: bool = True
    annualization_periods_per_year: dict[str, int] = Field(
        default_factory=lambda: {
            "crypto_daily": 365,
            "crypto_hourly": 8760,
            "crypto_4h": 2190,
            "crypto_1h": 8760,
            "crypto_15m": 35040,
            "crypto_5m": 105120,
            "crypto_1m": 525600,
        }
    )
    default_periods_per_year: int = 365
    compute_cagr: bool = True
    compute_annualized_volatility: bool = True
    compute_sharpe: bool = True
    compute_sortino: bool = True
    compute_calmar: bool = True
    compute_omega: bool = True
    compute_tail_ratio: bool = True
    compute_var_cvar: bool = True
    var_confidence: float = Field(default=0.95, ge=0.0, le=1.0)
    compute_skew_kurtosis: bool = True
    compute_payoff_ratio: bool = True
    compute_recovery_factor: bool = True
    compute_ulcer_index: bool = True
    compute_expectancy: bool = True
    compute_r_multiple_placeholder: bool = True
    min_observations_for_ratio_metrics: int = Field(default=30, ge=2)
    min_trades_for_trade_metrics: int = Field(default=5, ge=2)
    risk_free_rate_annual: float = 0.0


class BacktestReportingRollingConfig(BaseModel):
    enabled: bool = True
    windows: list[int] = Field(default_factory=lambda: [20, 50, 100])
    compute_rolling_return: bool = True
    compute_rolling_volatility: bool = True
    compute_rolling_sharpe: bool = True
    compute_rolling_drawdown: bool = True
    compute_rolling_win_rate: bool = True
    center_windows: Literal[False] = False  # strict constraint
    min_periods_ratio: float = 0.70


class BacktestPeriodicReturnsConfig(BaseModel):
    enabled: bool = True
    daily: bool = True
    weekly: bool = True
    monthly: bool = True
    quarterly: bool = True
    yearly: bool = True
    calendar_heatmap_table: bool = True
    use_resample: bool = True
    require_datetime_index: bool = True


class BacktestReportingBenchmarkConfig(BaseModel):
    enabled: bool = True
    compare_buy_and_hold: bool = True
    compare_cash: bool = True
    compare_equal_weight_placeholder: bool = False
    compute_excess_return: bool = True
    compute_tracking_error: bool = True
    compute_information_ratio: bool = True
    compute_alpha_beta_placeholder: bool = True
    require_same_date_range: bool = True
    benchmark_label: str = "buy_and_hold"


class BacktestReportingDrawdownConfig(BaseModel):
    enabled: bool = True
    top_n_drawdowns: int = Field(default=10, ge=1)
    compute_drawdown_duration: bool = True
    compute_recovery_time: bool = True
    compute_underwater_curve: bool = True
    compute_avg_drawdown: bool = True
    compute_max_drawdown: bool = True
    require_recovery_metadata: bool = True


class BacktestTradeDistributionConfig(BaseModel):
    enabled: bool = True
    compute_win_loss_distribution: bool = True
    compute_trade_return_histogram: bool = True
    histogram_bins: int = Field(default=20, ge=1, le=200)
    compute_best_worst_trades: bool = True
    top_n_trades: int = Field(default=10, ge=1)
    compute_consecutive_wins_losses: bool = True
    compute_holding_time_distribution: bool = True


class BacktestBreakdownConfig(BaseModel):
    enabled: bool = True
    by_regime: bool = True
    by_strategy_plugin: bool = True
    by_signal_score_tier: bool = True
    by_risk_status: bool = True
    by_direction: bool = True
    by_symbol: bool = True
    by_interval: bool = True
    min_trades_per_bucket_warning: int = 3


class BacktestCostAnalysisConfig(BaseModel):
    enabled: bool = True
    analyze_fees: bool = True
    analyze_slippage: bool = True
    compute_gross_vs_net: bool = True
    compute_cost_drag_pct: bool = True
    warn_high_cost_drag: bool = True
    high_cost_drag_pct: float = Field(default=25.0, ge=0.0, le=100.0)


class BacktestReportPackConfig(BaseModel):
    enabled: bool = True
    include_summary: bool = True
    include_metrics: bool = True
    include_rolling_metrics: bool = True
    include_periodic_returns: bool = True
    include_benchmark: bool = True
    include_drawdowns: bool = True
    include_trade_distribution: bool = True
    include_breakdowns: bool = True
    include_cost_analysis: bool = True
    include_quality: bool = True
    include_disclaimer: bool = True
    export_json: bool = True
    export_markdown: bool = True
    export_csv_tables: bool = True
    export_html_static_skeleton: Literal[False] = False  # MUST BE FALSE BY DEFAULT


class BacktestReportingAdapterOptionalConfig(BaseModel):
    enabled: bool = True
    fail_if_missing: bool = False
    compare_native_metrics: bool = True
    generate_external_report: bool = False


class BacktestReportingAdapterConfig(BaseModel):
    empyrical_optional: BacktestReportingAdapterOptionalConfig = (
        BacktestReportingAdapterOptionalConfig()
    )
    quantstats_optional: BacktestReportingAdapterOptionalConfig = (
        BacktestReportingAdapterOptionalConfig(generate_external_report=False)
    )


class BacktestReportingQualityConfig(BaseModel):
    reject_nan_inf_metrics: bool = True
    warn_low_observation_count: bool = True
    warn_low_trade_count: bool = True
    reject_missing_disclaimer: bool = True
    reject_missing_hashes: bool = True
    reject_mismatched_date_range: bool = True
    warn_metric_instability: bool = True
    reject_live_performance_claims: bool = True


class BacktestReportingConfig(BaseModel):
    enabled: bool = True
    output_dataset_name: str = "backtest_report_packs"
    cache_enabled: bool = True
    cache_dir: str = "data/backtest/reports_v2/cache"
    export_dir: str = "data/backtest/reports_v2/exports"
    report_dir: str = "data/backtest/reports_v2/reports"

    real_exchange_forbidden: Literal[True] = True
    no_live_claims: Literal[True] = True
    require_disclaimer: bool = True
    require_input_hash: bool = True
    require_config_hash: bool = True
    require_report_hash: bool = True

    metrics: BacktestReportingMetricsConfig = BacktestReportingMetricsConfig()
    rolling: BacktestReportingRollingConfig = BacktestReportingRollingConfig()
    periodic_returns: BacktestPeriodicReturnsConfig = BacktestPeriodicReturnsConfig()
    benchmark: BacktestReportingBenchmarkConfig = BacktestReportingBenchmarkConfig()
    drawdown: BacktestReportingDrawdownConfig = BacktestReportingDrawdownConfig()
    trade_distribution: BacktestTradeDistributionConfig = BacktestTradeDistributionConfig()
    breakdowns: BacktestBreakdownConfig = BacktestBreakdownConfig()
    costs: BacktestCostAnalysisConfig = BacktestCostAnalysisConfig()
    report_pack: BacktestReportPackConfig = BacktestReportPackConfig()
    adapters: BacktestReportingAdapterConfig = BacktestReportingAdapterConfig()
    quality: BacktestReportingQualityConfig = BacktestReportingQualityConfig()


class OptimizerModeConfig(BaseModel):
    default_method: Literal["grid", "random", "optuna_optional"] = "grid"
    allowed_methods: list[str] = Field(
        default_factory=lambda: ["grid", "random", "optuna_optional"]
    )
    deterministic: Literal[True] = True
    random_seed: int = 42
    max_trials: int = Field(default=100, ge=1, le=10000)
    max_grid_combinations: int = Field(default=200, ge=1, le=10000)
    max_parallel_trials: int = Field(default=1, le=1)
    parallel_execution_enabled: Literal[False] = False
    fail_fast: bool = False
    continue_on_trial_failure: bool = True


class OptimizerDataSplitConfig(BaseModel):
    enabled: bool = True
    split_method: str = "chronological"
    train_pct: float = Field(default=0.60, ge=0.0, le=1.0)
    validation_pct: float = Field(default=0.20, ge=0.0, le=1.0)
    test_pct: float = Field(default=0.20, ge=0.0, le=1.0)
    min_train_rows: int = Field(default=500, gt=0)
    min_validation_rows: int = Field(default=200, gt=0)
    min_test_rows: int = Field(default=200, gt=0)
    embargo_bars: int = Field(default=0, ge=0)
    purge_overlapping_labels: bool = False
    time_series_cv_enabled: bool = True
    time_series_cv_splits: int = 3
    walk_forward_skeleton_enabled: bool = True
    walk_forward_full_run_deferred: Literal[True] = True

    @model_validator(mode="after")
    def validate_split_pct(self) -> "OptimizerDataSplitConfig":
        total = self.train_pct + self.validation_pct + self.test_pct
        if abs(total - 1.0) > 1e-6:
            raise ValueError("train_pct + validation_pct + test_pct must equal 1.0")
        return self


class OptimizerSearchSpaceConfig(BaseModel):
    max_parameters: int = Field(default=20, ge=1, le=100)
    max_values_per_parameter: int = 20
    reject_empty_space: bool = True
    reject_unbounded_space: bool = True
    require_parameter_descriptions: bool = True
    allow_strategy_params: bool = True
    allow_signal_params: bool = True
    allow_risk_params: bool = True
    allow_backtest_params: bool = True
    allow_execution_params: Literal[False] = False
    allow_live_params: Literal[False] = False


class OptimizerObjectiveComponentConfig(BaseModel):
    total_return_weight: float = 0.20
    sharpe_weight: float = 0.15
    sortino_weight: float = 0.10
    calmar_weight: float = 0.10
    max_drawdown_weight: float = -0.20
    profit_factor_weight: float = 0.10
    expectancy_weight: float = 0.10
    trade_count_weight: float = 0.05
    stability_weight: float = 0.10
    cost_drag_weight: float = -0.10
    overfit_penalty_weight: float = -0.30


class OptimizerObjectiveConfig(BaseModel):
    primary_metric: str = "robust_score"
    maximize: bool = True
    components: OptimizerObjectiveComponentConfig = OptimizerObjectiveComponentConfig()
    min_trade_count: int = 10
    min_validation_trade_count: int = 5
    max_drawdown_hard_limit_pct: float = 35.0
    max_cost_drag_pct: float = 30.0
    score_clamp_min: float = -100.0
    score_clamp_max: float = 100.0

    @model_validator(mode="after")
    def validate_clamp(self) -> "OptimizerObjectiveConfig":
        if self.score_clamp_min >= self.score_clamp_max:
            raise ValueError("score_clamp_min must be strictly less than score_clamp_max")
        return self


class OptimizerOverfitConfig(BaseModel):
    enabled: bool = True
    reject_if_train_validation_gap_too_high: bool = True
    max_train_validation_return_gap_pct: float = 50.0
    max_train_validation_sharpe_gap: float = 1.5
    reject_if_validation_bad: bool = True
    reject_if_test_bad: bool = False
    validation_score_min: float = 0.0
    test_score_min_warning: float = 0.0
    penalize_parameter_complexity: bool = True
    complexity_penalty_per_parameter: float = 0.5
    penalize_low_trade_count: bool = True
    penalize_high_drawdown: bool = True
    penalize_high_cost_drag: bool = True
    warn_best_trial_only_good_on_train: bool = True
    require_validation_rank_consistency: bool = True


class OptimizerRobustnessConfig(BaseModel):
    enabled: bool = True
    compute_rank_stability: bool = True
    compute_metric_dispersion: bool = True
    compute_neighbor_sensitivity: bool = True
    neighbor_distance_numeric_pct: float = 20.0
    top_n_trials_for_robustness: int = 10
    min_robustness_score: float = 0.0
    warn_fragile_optimum: bool = True


class OptimizerOptunaOptionalConfig(BaseModel):
    enabled: bool = False
    fail_if_missing: Literal[False] = False
    sampler: str = "tpe"
    pruner: str = "median"
    n_trials: int = 50
    timeout_seconds: int | None = None
    direction: str = "maximize"
    study_name_prefix: str = "binance50_optimizer"
    persistent_storage_enabled: bool = False


class OptimizerQualityConfig(BaseModel):
    reject_no_trials: bool = True
    reject_all_trials_failed: bool = True
    reject_missing_objective: bool = True
    reject_nan_inf_scores: bool = True
    reject_missing_split_metadata: bool = True
    reject_missing_reproducibility_hash: bool = True
    warn_low_trial_count: bool = True
    min_trial_count_warning: int = 10
    warn_no_validation_set: bool = True
    reject_live_or_paper_intent: bool = True


class OptimizerConfig(BaseModel):
    enabled: bool = True
    output_dataset_name: str = "optimization_trials"
    cache_enabled: bool = True
    cache_dir: str = "data/optimizer/cache"
    export_dir: str = "data/optimizer/exports"
    reports_dir: str = "data/optimizer/reports"

    real_exchange_forbidden: Literal[True] = True
    paper_trade_forbidden: Literal[True] = True
    live_trade_forbidden: Literal[True] = True
    order_creation_forbidden: Literal[True] = True
    api_key_forbidden: Literal[True] = True
    signed_request_forbidden: Literal[True] = True
    dashboard_forbidden: Literal[True] = True

    mode: OptimizerModeConfig = OptimizerModeConfig()
    data_split: OptimizerDataSplitConfig = OptimizerDataSplitConfig()
    search_space: OptimizerSearchSpaceConfig = OptimizerSearchSpaceConfig()
    default_search_spaces: dict[str, dict[str, list[float | int | str | bool]]] = Field(
        default_factory=lambda: {
            "strategy": {
                "trend_following.min_adx": [18.0, 20.0, 22.0, 25.0],
                "mean_reversion.rsi_oversold": [25.0, 30.0, 35.0],
                "mean_reversion.rsi_overbought": [65.0, 70.0, 75.0],
                "momentum_continuation.rsi_min": [48.0, 50.0, 55.0],
            },
            "signals": {
                "thresholds.research_candidate_min": [45.0, 50.0, 55.0],
                "thresholds.risk_review_min": [60.0, 65.0, 70.0],
                "confluence.same_direction_bonus_per_plugin": [3.0, 5.0, 7.0],
            },
            "risk": {
                "decision.min_final_risk_score": [55.0, 60.0, 65.0],
                "volatility.high_volatility_penalty": [10.0, 15.0, 20.0],
                "conflicts.high_conflict_penalty": [10.0, 20.0, 30.0],
            },
            "backtest": {
                "sizing.fixed_notional_usdt": [25.0, 50.0, 75.0],
                "slippage.default_slippage_bps": [1.0, 2.0, 5.0],
                "exits.max_holding_bars": [50, 100, 150],
            },
        }
    )
    objective: OptimizerObjectiveConfig = OptimizerObjectiveConfig()
    overfit: OptimizerOverfitConfig = OptimizerOverfitConfig()
    robustness: OptimizerRobustnessConfig = OptimizerRobustnessConfig()
    optuna_optional: OptimizerOptunaOptionalConfig = OptimizerOptunaOptionalConfig()
    quality: OptimizerQualityConfig = OptimizerQualityConfig()

    @model_validator(mode="after")
    def validate_dataset_name(self) -> "OptimizerConfig":
        if not re.match(r"^[a-zA-Z0-9_-]+$", self.output_dataset_name):
            raise ValueError(
                "output_dataset_name must contain only alphanumeric characters, underscores, and dashes"
            )
        return self


class WalkForwardModeConfig(BaseModel):
    default_mode: Literal["rolling_window", "expanding_window", "anchored_expanding"] = (
        "rolling_window"
    )
    allowed_modes: list[str] = ["rolling_window", "expanding_window", "anchored_expanding"]
    deterministic: bool = True
    random_seed: int = 42
    max_windows: int = 20
    min_windows_required: int = 3
    run_optimizer_per_window: bool = True
    allow_fixed_params_mode: bool = True
    max_optimizer_trials_per_window: int = 50
    parallel_windows_enabled: bool = False
    max_parallel_windows: int = 1
    continue_on_window_failure: bool = True


class WalkForwardWindowConfig(BaseModel):
    train_bars: int = 2000
    validation_bars: int = 500
    test_bars: int = 500
    step_bars: int = 500
    min_train_bars: int = 1000
    min_validation_bars: int = 200
    min_test_bars: int = 200
    embargo_bars: int = 0
    gap_bars_between_train_validation: int = 0
    gap_bars_between_validation_test: int = 0
    allow_overlapping_oos_windows: bool = False
    require_equal_oos_duration: bool = True


class WalkForwardExpandingConfig(BaseModel):
    initial_train_bars: int = 2000
    train_expansion_step_bars: int = 500
    max_train_bars: int | None = None
    anchored_start: bool = True


class WalkForwardOptimizerConfig(BaseModel):
    method: Literal["grid", "random", "optuna_optional"] = "grid"
    inherit_optimizer_config: bool = True
    override_max_trials: int = 50
    select_best_by: str = "validation_robust_score"
    use_test_for_selection: bool = False
    require_overfit_guard: bool = True
    require_robustness_guard: bool = True
    reject_overfit_trials: bool = True


class WalkForwardOOSConfig(BaseModel):
    enabled: bool = True
    stitch_oos_equity: bool = True
    compound_oos_equity: bool = False
    reset_capital_each_window: bool = True
    starting_cash_usdt: float = 1000.0
    require_oos_backtest_report: bool = True
    min_oos_trade_count_warning: int = 3
    aggregate_oos_metrics: bool = True


class WalkForwardStabilityConfig(BaseModel):
    enabled: bool = True
    compute_window_score_stability: bool = True
    compute_oos_return_stability: bool = True
    compute_oos_drawdown_stability: bool = True
    compute_trade_count_stability: bool = True
    compute_parameter_stability: bool = True
    min_stability_score: float = 0.0
    max_stability_score: float = 100.0
    warn_unstable_windows: bool = True


class WalkForwardDegradationConfig(BaseModel):
    enabled: bool = True
    compare_train_validation_oos: bool = True
    max_validation_to_oos_score_drop: float = 40.0
    max_validation_to_oos_return_drop_pct: float = 50.0
    max_validation_to_oos_sharpe_drop: float = 1.5
    warn_severe_degradation: bool = True


class WalkForwardParameterDriftConfig(BaseModel):
    enabled: bool = True
    compute_numeric_drift: bool = True
    compute_categorical_drift: bool = True
    warn_high_drift: bool = True
    high_drift_threshold: float = 0.60
    stable_parameter_bonus: bool = True


class WalkForwardRegimeAnalysisConfig(BaseModel):
    enabled: bool = True
    analyze_oos_by_regime: bool = True
    analyze_window_regime_distribution: bool = True
    warn_regime_concentration: bool = True
    max_single_regime_oos_ratio: float = 0.80
    warn_regime_shift_between_train_oos: bool = True


class WalkForwardRobustnessConfig(BaseModel):
    enabled: bool = True
    compute_window_rank_consistency: bool = True
    compute_best_trial_recurrence: bool = True
    compute_oos_metric_dispersion: bool = True
    compute_oos_hit_rate_consistency: bool = True
    compute_walkforward_robust_score: bool = True
    min_walkforward_robust_score_warning: float = 40.0


class WalkForwardLeakageConfig(BaseModel):
    prevent_lookahead_bias: bool = True
    reject_future_columns: bool = True
    reject_target_columns: bool = True
    reject_label_columns: bool = True
    reject_split_overlap: bool = True
    reject_test_selection: bool = True
    reject_forward_alignment: bool = True
    reject_nearest_alignment: bool = True
    require_backward_asof_alignment: bool = True
    reject_same_bar_fill: bool = True
    reject_oos_overlap_when_disabled: bool = True


class WalkForwardQualityConfig(BaseModel):
    reject_no_windows: bool = True
    reject_all_windows_failed: bool = True
    reject_missing_oos_results: bool = True
    reject_missing_window_metadata: bool = True
    reject_missing_best_trial: bool = True
    reject_missing_hashes: bool = True
    reject_nan_inf_metrics: bool = True
    warn_low_window_count: bool = True
    warn_low_oos_trade_count: bool = True
    warn_high_parameter_drift: bool = True
    warn_high_degradation: bool = True
    reject_live_or_paper_intent: bool = True


class WalkForwardConfig(BaseModel):
    enabled: bool = True
    output_dataset_name: str = "walkforward_runs"
    cache_enabled: bool = True
    cache_dir: str = "data/walkforward/cache"
    export_dir: str = "data/walkforward/exports"
    reports_dir: str = "data/walkforward/reports"

    real_exchange_forbidden: bool = True
    paper_trade_forbidden: bool = True
    live_trade_forbidden: bool = True
    order_creation_forbidden: bool = True
    api_key_forbidden: bool = True
    signed_request_forbidden: bool = True
    dashboard_forbidden: bool = True

    mode: WalkForwardModeConfig = Field(default_factory=WalkForwardModeConfig)
    windows: WalkForwardWindowConfig = Field(default_factory=WalkForwardWindowConfig)
    expanding: WalkForwardExpandingConfig = Field(default_factory=WalkForwardExpandingConfig)
    optimizer: WalkForwardOptimizerConfig = Field(default_factory=WalkForwardOptimizerConfig)
    oos: WalkForwardOOSConfig = Field(default_factory=WalkForwardOOSConfig)
    stability: WalkForwardStabilityConfig = Field(default_factory=WalkForwardStabilityConfig)
    degradation: WalkForwardDegradationConfig = Field(default_factory=WalkForwardDegradationConfig)
    parameter_drift: WalkForwardParameterDriftConfig = Field(
        default_factory=WalkForwardParameterDriftConfig
    )
    regime_analysis: WalkForwardRegimeAnalysisConfig = Field(
        default_factory=WalkForwardRegimeAnalysisConfig
    )
    robustness: WalkForwardRobustnessConfig = Field(default_factory=WalkForwardRobustnessConfig)
    leakage: WalkForwardLeakageConfig = Field(default_factory=WalkForwardLeakageConfig)
    quality: WalkForwardQualityConfig = Field(default_factory=WalkForwardQualityConfig)

    @model_validator(mode="after")
    def validate_safety_rules(self) -> "WalkForwardConfig":
        if not self.real_exchange_forbidden:
            raise ValueError("real_exchange_forbidden must be True in walkforward")
        if not self.paper_trade_forbidden:
            raise ValueError("paper_trade_forbidden must be True in walkforward")
        if not self.live_trade_forbidden:
            raise ValueError("live_trade_forbidden must be True in walkforward")
        if not self.order_creation_forbidden:
            raise ValueError("order_creation_forbidden must be True in walkforward")
        if not self.api_key_forbidden:
            raise ValueError("api_key_forbidden must be True in walkforward")
        if not self.signed_request_forbidden:
            raise ValueError("signed_request_forbidden must be True in walkforward")
        if not self.dashboard_forbidden:
            raise ValueError("dashboard_forbidden must be True in walkforward")
        if not self.mode.deterministic:
            raise ValueError("deterministic must be True in walkforward")

        if self.mode.parallel_windows_enabled and self.mode.max_parallel_windows < 1:
            raise ValueError("max_parallel_windows must be >= 1")

        if self.windows.train_bars < self.windows.min_train_bars:
            raise ValueError("train_bars cannot be less than min_train_bars")
        if self.windows.validation_bars < self.windows.min_validation_bars:
            raise ValueError("validation_bars cannot be less than min_validation_bars")
        if self.windows.validation_bars <= 0:
            raise ValueError("validation_bars must be > 0")
        if self.windows.test_bars <= 0:
            raise ValueError("test_bars must be > 0")
        if self.windows.step_bars <= 0:
            raise ValueError("step_bars must be > 0")

        if self.mode.min_windows_required < 2:
            raise ValueError("min_windows_required must be >= 2")
        if self.mode.max_windows < self.mode.min_windows_required:
            raise ValueError("max_windows must be >= min_windows_required")

        if self.optimizer.use_test_for_selection:
            raise ValueError("use_test_for_selection must be False in walkforward")
        if not self.optimizer.require_overfit_guard:
            raise ValueError("require_overfit_guard must be True in walkforward")
        if not self.optimizer.require_robustness_guard:
            raise ValueError("require_robustness_guard must be True in walkforward")

        if not self.leakage.reject_split_overlap:
            raise ValueError("reject_split_overlap must be True in walkforward")
        if not self.leakage.reject_test_selection:
            raise ValueError("reject_test_selection must be True in walkforward")
        if not self.leakage.reject_forward_alignment:
            raise ValueError("reject_forward_alignment must be True in walkforward")
        if not self.leakage.reject_nearest_alignment:
            raise ValueError("reject_nearest_alignment must be True in walkforward")
        if not self.leakage.require_backward_asof_alignment:
            raise ValueError("require_backward_asof_alignment must be True in walkforward")
        if not self.leakage.reject_same_bar_fill:
            raise ValueError("reject_same_bar_fill must be True in walkforward")

        if not self.output_dataset_name.replace("_", "").isalnum():
            raise ValueError("output_dataset_name contains unsafe characters")

        return self



class MLDatasetSourceConfig(BaseModel):
    use_indicator_v1: bool = True
    use_indicator_v2: bool = True
    use_strategy_candidates: bool = False
    use_scored_signals: bool = True
    use_regimes: bool = True
    use_risk_assessments: bool = True
    use_backtest_metadata: bool = False
    use_walkforward_metadata: bool = False
    require_source_hashes: bool = True
    require_source_timestamps: bool = True

class MLFeatureSelectionConfig(BaseModel):
    enabled: bool = True
    include_prefixes: list[str] = Field(default_factory=list)
    exclude_prefixes: list[str] = Field(default_factory=list)
    required_base_columns: list[str] = Field(default_factory=list)
    max_feature_columns: int = 1500
    min_feature_columns: int = 10
    reject_all_nan_features: bool = True
    reject_constant_features: bool = False
    warn_constant_features: bool = True
    max_nan_ratio_per_feature: float = Field(default=0.40, ge=0.0, le=1.0)
    max_inf_count: int = 0
    allow_object_features: bool = False
    allow_boolean_features: bool = True
    allow_categorical_features: bool = True
    categorical_encoding_deferred: bool = True

    @model_validator(mode="after")
    def validate_feature_counts(self) -> "MLFeatureSelectionConfig":
        if self.max_feature_columns <= self.min_feature_columns:
            raise ValueError("max_feature_columns must be > min_feature_columns")
        return self

class MLLabelTripleBarrierConfig(BaseModel):
    enabled: bool = False
    profit_take_pct: float = 1.0
    stop_loss_pct: float = 0.5
    max_holding_bars: int = 20
    full_engine_deferred: bool = True

class MLLabelConfig(BaseModel):
    enabled: bool = True
    default_label_type: str = "forward_return_classification"
    allowed_label_types: list[str] = Field(default_factory=list)
    horizons_bars: list[int] = Field(default_factory=lambda: [5])
    default_horizon_bars: int = 5
    return_source: str = "close"
    classification_threshold_pct: float = Field(default=0.20, ge=0.0)
    neutral_zone_pct: float = Field(default=0.05, ge=0.0)
    include_neutral_class: bool = True
    label_column_prefix: str = "label_"
    future_return_column_prefix: str = "label_future_return_"
    allow_label_columns_in_features: bool = False
    drop_rows_without_label: bool = True
    drop_last_horizon_rows: bool = True
    triple_barrier: MLLabelTripleBarrierConfig = Field(default_factory=MLLabelTripleBarrierConfig)

    @model_validator(mode="after")
    def validate_horizons(self) -> "MLLabelConfig":
        for h in self.horizons_bars:
            if h <= 0:
                raise ValueError("all horizons must be > 0")
        if self.default_horizon_bars not in self.horizons_bars:
            raise ValueError("default_horizon_bars must be in horizons_bars")
        if self.allow_label_columns_in_features:
            raise ValueError("allow_label_columns_in_features must be False")
        if not self.drop_last_horizon_rows:
            raise ValueError("drop_last_horizon_rows must be True")
        return self

class MLSplitConfig(BaseModel):
    enabled: bool = True
    split_method: str = "chronological"
    train_pct: float = Field(default=0.60, ge=0.0, le=1.0)
    validation_pct: float = Field(default=0.20, ge=0.0, le=1.0)
    test_pct: float = Field(default=0.20, ge=0.0, le=1.0)
    min_train_rows: int = 500
    min_validation_rows: int = 200
    min_test_rows: int = 200
    time_series_cv_enabled: bool = True
    time_series_cv_splits: int = 3
    embargo_bars: int = 0
    purge_overlapping_labels: bool = True
    test_set_for_final_report_only: bool = True
    reject_split_overlap: bool = True
    reject_test_selection: bool = True

    @model_validator(mode="after")
    def validate_split_pcts(self) -> "MLSplitConfig":
        if abs(self.train_pct + self.validation_pct + self.test_pct - 1.0) > 1e-6:
            raise ValueError("train_pct + validation_pct + test_pct must equal 1.0")
        return self

class MLPreprocessingImputationConfig(BaseModel):
    enabled: bool = True
    strategy: str = "median_train_only"
    allow_bfill: bool = False
    allow_ffill: bool = True
    fit_imputer_train_only: bool = True

    @model_validator(mode="after")
    def validate_imputation(self) -> "MLPreprocessingImputationConfig":
        if self.allow_bfill:
            raise ValueError("allow_bfill must be False")
        return self

class MLPreprocessingClippingConfig(BaseModel):
    enabled: bool = True
    method: str = "train_quantile"
    lower_quantile: float = Field(default=0.001, ge=0.0, le=0.5)
    upper_quantile: float = Field(default=0.999, ge=0.5, le=1.0)
    fit_clipper_train_only: bool = True

class MLPreprocessingCategoricalConfig(BaseModel):
    enabled: bool = False
    encoding_deferred: bool = True

class MLPreprocessingConfig(BaseModel):
    enabled: bool = True
    fit_transform_train_only: bool = True
    transform_validation_test_only: bool = True
    scaler: str = "standard"
    allowed_scalers: list[str] = Field(default_factory=list)
    imputation: MLPreprocessingImputationConfig = Field(default_factory=MLPreprocessingImputationConfig)
    clipping: MLPreprocessingClippingConfig = Field(default_factory=MLPreprocessingClippingConfig)
    categorical: MLPreprocessingCategoricalConfig = Field(default_factory=MLPreprocessingCategoricalConfig)
    persist_preprocessor: bool = True
    preprocessor_registry_enabled: bool = True

    @model_validator(mode="after")
    def validate_preprocessing(self) -> "MLPreprocessingConfig":
        if not self.fit_transform_train_only:
            raise ValueError("fit_transform_train_only must be True")
        if not self.transform_validation_test_only:
            raise ValueError("transform_validation_test_only must be True")
        return self

class MLAlignmentConfig(BaseModel):
    enabled: bool = True
    method: str = "backward_asof"
    reject_forward_alignment: bool = True
    reject_nearest_alignment: bool = True
    require_no_future_join: bool = True
    tolerance_bars: int = 1
    require_closed_candles: bool = True

    @model_validator(mode="after")
    def validate_alignment(self) -> "MLAlignmentConfig":
        if not self.reject_forward_alignment:
            raise ValueError("reject_forward_alignment must be True")
        if not self.reject_nearest_alignment:
            raise ValueError("reject_nearest_alignment must be True")
        return self

class MLLeakageConfig(BaseModel):
    prevent_lookahead_bias: bool = True
    reject_future_columns_in_features: bool = True
    reject_target_columns_in_features: bool = True
    reject_label_columns_in_features: bool = True
    reject_next_columns_in_features: bool = True
    reject_forward_columns_in_features: bool = True
    reject_negative_shift_features: bool = True
    allow_forward_shift_only_for_labels: bool = True
    reject_global_scaler_fit: bool = True
    reject_global_imputer_fit: bool = True
    reject_global_clipper_fit: bool = True
    reject_test_fit: bool = True
    reject_validation_fit: bool = True
    reject_same_bar_label_as_feature: bool = True

    @model_validator(mode="after")
    def validate_leakage(self) -> "MLLeakageConfig":
        if not self.reject_global_scaler_fit:
            raise ValueError("reject_global_scaler_fit must be True")
        if not self.reject_test_fit:
            raise ValueError("reject_test_fit must be True")
        if not self.reject_validation_fit:
            raise ValueError("reject_validation_fit must be True")
        return self


class MLQualityConfig(BaseModel):
    reject_empty_dataset: bool = True
    reject_missing_labels: bool = True
    reject_missing_features: bool = True
    reject_single_class_labels: bool = False
    warn_single_class_labels: bool = True
    warn_class_imbalance: bool = True
    max_majority_class_ratio: float = Field(default=0.85, ge=0.5, le=1.0)
    reject_nan_inf_features: bool = True
    reject_nan_inf_labels: bool = True
    reject_missing_split_metadata: bool = True
    reject_missing_hashes: bool = True
    reject_leakage_warnings: bool = True
    warn_low_row_count: bool = True
    min_total_rows_warning: int = 1000

class MLDatasetConfig(BaseModel):
    enabled: bool = True
    output_dataset_name: str = "ml_datasets"
    cache_enabled: bool = True
    cache_dir: str = "data/ml/datasets/cache"
    export_dir: str = "data/ml/datasets/exports"
    registry_dir: str = "data/ml/datasets/registry"

    real_exchange_forbidden: bool = True
    paper_trade_forbidden: bool = True
    live_trade_forbidden: bool = True
    order_creation_forbidden: bool = True
    api_key_forbidden: bool = True
    signed_request_forbidden: bool = True
    dashboard_forbidden: bool = True
    model_training_deferred: bool = True
    prediction_deferred: bool = True

    sources: MLDatasetSourceConfig = Field(default_factory=MLDatasetSourceConfig)
    feature_selection: MLFeatureSelectionConfig = Field(default_factory=MLFeatureSelectionConfig)
    labels: MLLabelConfig = Field(default_factory=MLLabelConfig)
    splits: MLSplitConfig = Field(default_factory=MLSplitConfig)
    preprocessing: MLPreprocessingConfig = Field(default_factory=MLPreprocessingConfig)
    alignment: MLAlignmentConfig = Field(default_factory=MLAlignmentConfig)
    leakage: MLLeakageConfig = Field(default_factory=MLLeakageConfig)
    quality: MLQualityConfig = Field(default_factory=MLQualityConfig)

    @model_validator(mode="after")
    def validate_safety_flags(self) -> "MLDatasetConfig":
        if not self.real_exchange_forbidden:
            raise ValueError("real_exchange_forbidden must be True")
        if not self.paper_trade_forbidden:
            raise ValueError("paper_trade_forbidden must be True")
        if not self.live_trade_forbidden:
            raise ValueError("live_trade_forbidden must be True")
        if not self.order_creation_forbidden:
            raise ValueError("order_creation_forbidden must be True")
        if not self.api_key_forbidden:
            raise ValueError("api_key_forbidden must be True")
        if not self.signed_request_forbidden:
            raise ValueError("signed_request_forbidden must be True")
        if not self.dashboard_forbidden:
            raise ValueError("dashboard_forbidden must be True")
        if not self.model_training_deferred:
            raise ValueError("model_training_deferred must be True")
        if not self.prediction_deferred:
            raise ValueError("prediction_deferred must be True")
        if not re.match(r"^[a-zA-Z0-9_-]+$", self.output_dataset_name):
            raise ValueError("output_dataset_name is not safe")
        return self

class MLTrainingDatasetConfig(BaseModel):
    require_ml_dataset_manifest: bool = True
    require_leakage_free_dataset: bool = True
    require_quality_passed_dataset: bool = True
    allowed_label_types: list[str] = Field(default_factory=list)
    default_label_column: str = "label_forward_return_classification_5"
    require_split_metadata: bool = True
    require_preprocessor_metadata: bool = True
    reject_if_feature_contains_label: bool = True
    reject_if_feature_contains_future: bool = True
    reject_if_feature_contains_target: bool = True
    reject_if_missing_train_validation_test: bool = True

class MLTrainingTaskConfig(BaseModel):
    default_task_type: str = "classification"
    allowed_task_types: list[str] = Field(default_factory=list)
    multiclass_enabled: bool = True
    binary_enabled: bool = True
    regression_default_enabled: bool = False
    ranking_deferred: bool = True

class MLLogisticRegressionConfig(BaseModel):
    enabled: bool = True
    max_iter: int = 1000
    class_weight: str = "balanced"
    solver: str = "lbfgs"
    C: float = 1.0

class MLRandomForestClassifierConfig(BaseModel):
    enabled: bool = True
    n_estimators: int = 200
    max_depth: int = 6
    min_samples_leaf: int = 20
    class_weight: str = "balanced_subsample"
    random_state: int = 42
    n_jobs: int = 1

class MLHistGradientBoostingConfig(BaseModel):
    enabled: bool = True
    max_iter: int = 200
    max_leaf_nodes: int = 31
    learning_rate: float = 0.05
    l2_regularization: float = 0.0
    random_state: int = 42

class MLDummyClassifierConfig(BaseModel):
    enabled: bool = True
    strategy: str = "most_frequent"

class MLTrainingModelsConfig(BaseModel):
    enabled_models: list[str] = Field(default_factory=list)
    default_model: str = "logistic_regression"
    allow_regression_skeletons: bool = True
    random_state: int = 42
    n_jobs: int = 1
    max_fit_seconds_per_model: int = 300
    max_models_per_run: int = Field(default=10, ge=1, le=50)
    allow_gpu: bool = False
    require_deterministic_models: bool = True

    logistic_regression: MLLogisticRegressionConfig = Field(default_factory=MLLogisticRegressionConfig)
    random_forest_classifier: MLRandomForestClassifierConfig = Field(default_factory=MLRandomForestClassifierConfig)
    hist_gradient_boosting_classifier: MLHistGradientBoostingConfig = Field(default_factory=MLHistGradientBoostingConfig)
    dummy_classifier: MLDummyClassifierConfig = Field(default_factory=MLDummyClassifierConfig)

class MLTrainingValidationConfig(BaseModel):
    enabled: bool = True
    method: str = "time_series_split"
    use_existing_ml_splits: bool = True
    train_split_name: str = "train"
    validation_split_name: str = "validation"
    test_split_name: str = "test"
    time_series_cv_enabled: bool = True
    time_series_cv_splits: int = 3
    test_set_final_report_only: bool = True
    reject_test_selection: bool = True
    reject_split_overlap: bool = True
    require_chronological_order: bool = True
    min_train_rows: int = 500
    min_validation_rows: int = 200
    min_test_rows: int = 200
    min_class_count_per_split: int = 2
    min_samples_per_class_warning: int = 25

class MLCalibrationConfig(BaseModel):
    enabled: bool = True
    calibrate_classifiers: bool = True
    method: str = "sigmoid"
    allowed_methods: list[str] = Field(default_factory=list)
    calibration_split: str = "validation"
    fit_calibrator_on_test_forbidden: bool = True
    require_calibration_report: bool = True
    reliability_bins: int = Field(default=10, ge=2, le=50)
    compute_brier_score: bool = True
    compute_expected_calibration_error: bool = True
    warn_uncalibrated_probabilities: bool = True
    isotonic_min_samples_warning: int = 1000

class MLClassificationMetricsConfig(BaseModel):
    compute_accuracy: bool = True
    compute_balanced_accuracy: bool = True
    compute_precision_recall_f1: bool = True
    compute_roc_auc: bool = True
    compute_pr_auc: bool = True
    compute_log_loss: bool = True
    compute_brier_score: bool = True
    compute_confusion_matrix: bool = True
    compute_classification_report: bool = True
    average: str = "weighted"
    zero_division: int = 0

class MLRegressionMetricsConfig(BaseModel):
    compute_mae: bool = True
    compute_rmse: bool = True
    compute_r2: bool = True
    compute_directional_accuracy: bool = True
    regression_deferred: bool = True

class MLTrainingMetricsConfig(BaseModel):
    classification: MLClassificationMetricsConfig = Field(default_factory=MLClassificationMetricsConfig)
    regression: MLRegressionMetricsConfig = Field(default_factory=MLRegressionMetricsConfig)

class MLFeatureImportanceConfig(BaseModel):
    enabled: bool = True
    native_model_importance: bool = True
    permutation_importance: bool = True
    permutation_n_repeats: int = 5
    permutation_random_state: int = 42
    permutation_split: str = "validation"
    max_features_reported: int = Field(default=100, ge=1, le=1000)
    warn_high_cardinality_importance_bias: bool = True

class MLTrainingOverfitConfig(BaseModel):
    enabled: bool = True
    compare_train_validation: bool = True
    max_train_validation_metric_gap: float = 0.25
    max_train_validation_auc_gap: float = 0.20
    warn_if_train_much_better: bool = True
    reject_if_validation_worse_than_dummy: bool = False
    warn_if_validation_worse_than_dummy: bool = True
    warn_if_test_much_worse_than_validation: bool = True
    test_degradation_warning_gap: float = 0.20

class MLModelRegistryConfig(BaseModel):
    enabled: bool = True
    active_model_serving_forbidden: bool = True
    auto_promote_forbidden: bool = True
    require_model_card: bool = True
    require_training_manifest: bool = True
    require_dataset_manifest_link: bool = True
    require_reproducibility_hashes: bool = True
    persist_model_artifacts: bool = True
    artifact_format: str = "joblib"
    persist_pickled_objects_warning: bool = True
    allow_loading_untrusted_artifacts: bool = False

class MLTrainingQualityConfig(BaseModel):
    reject_no_models_trained: bool = True
    reject_all_models_failed: bool = True
    reject_missing_metrics: bool = True
    reject_missing_calibration_report: bool = False
    reject_missing_model_card: bool = True
    reject_missing_dataset_manifest: bool = True
    reject_missing_hashes: bool = True
    reject_nan_inf_metrics: bool = True
    warn_low_sample_count: bool = True
    warn_class_imbalance: bool = True
    warn_single_class_split: bool = True
    reject_single_class_train: bool = True
    reject_single_class_validation: bool = False
    warn_uncalibrated_model: bool = True
    reject_live_or_paper_intent: bool = True

class MLTrainingConfig(BaseModel):
    enabled: bool = True
    output_dataset_name: str = "ml_training_runs"
    cache_enabled: bool = True
    cache_dir: str = "data/ml/training/cache"
    export_dir: str = "data/ml/training/exports"
    registry_dir: str = "data/ml/training/registry"
    artifacts_dir: str = "data/ml/training/artifacts"
    reports_dir: str = "data/ml/training/reports"

    real_exchange_forbidden: bool = True
    paper_trade_forbidden: bool = True
    live_trade_forbidden: bool = True
    order_creation_forbidden: bool = True
    api_key_forbidden: bool = True
    signed_request_forbidden: bool = True
    dashboard_forbidden: bool = True
    prediction_serving_deferred: bool = True
    execution_integration_forbidden: bool = True
    auto_strategy_update_forbidden: bool = True

    dataset: MLTrainingDatasetConfig = Field(default_factory=MLTrainingDatasetConfig)
    task: MLTrainingTaskConfig = Field(default_factory=MLTrainingTaskConfig)
    models: MLTrainingModelsConfig = Field(default_factory=MLTrainingModelsConfig)
    validation: MLTrainingValidationConfig = Field(default_factory=MLTrainingValidationConfig)
    calibration: MLCalibrationConfig = Field(default_factory=MLCalibrationConfig)
    metrics: MLTrainingMetricsConfig = Field(default_factory=MLTrainingMetricsConfig)
    feature_importance: MLFeatureImportanceConfig = Field(default_factory=MLFeatureImportanceConfig)
    overfit: MLTrainingOverfitConfig = Field(default_factory=MLTrainingOverfitConfig)
    registry: MLModelRegistryConfig = Field(default_factory=MLModelRegistryConfig)
    quality: MLTrainingQualityConfig = Field(default_factory=MLTrainingQualityConfig)

    @model_validator(mode="after")
    def validate_safety_flags(self) -> "MLTrainingConfig":
        if not self.real_exchange_forbidden:
            raise ValueError("real_exchange_forbidden must be True")
        if not self.paper_trade_forbidden:
            raise ValueError("paper_trade_forbidden must be True")
        if not self.live_trade_forbidden:
            raise ValueError("live_trade_forbidden must be True")
        if not self.order_creation_forbidden:
            raise ValueError("order_creation_forbidden must be True")
        if not self.api_key_forbidden:
            raise ValueError("api_key_forbidden must be True")
        if not self.signed_request_forbidden:
            raise ValueError("signed_request_forbidden must be True")
        if not self.dashboard_forbidden:
            raise ValueError("dashboard_forbidden must be True")
        if not self.prediction_serving_deferred:
            raise ValueError("prediction_serving_deferred must be True")
        if not self.execution_integration_forbidden:
            raise ValueError("execution_integration_forbidden must be True")
        if not self.auto_strategy_update_forbidden:
            raise ValueError("auto_strategy_update_forbidden must be True")

        if not self.dataset.require_ml_dataset_manifest:
            raise ValueError("require_ml_dataset_manifest must be True")
        if not self.dataset.require_leakage_free_dataset:
            raise ValueError("require_leakage_free_dataset must be True")
        if not self.dataset.require_quality_passed_dataset:
            raise ValueError("require_quality_passed_dataset must be True")

        if not self.validation.reject_test_selection:
            raise ValueError("reject_test_selection must be True")
        if not self.calibration.fit_calibrator_on_test_forbidden:
            raise ValueError("fit_calibrator_on_test_forbidden must be True")

        if not self.registry.active_model_serving_forbidden:
            raise ValueError("active_model_serving_forbidden must be True")
        if not self.registry.auto_promote_forbidden:
            raise ValueError("auto_promote_forbidden must be True")
        if self.registry.allow_loading_untrusted_artifacts:
            raise ValueError("allow_loading_untrusted_artifacts must be False")

        if not re.match(r"^[a-zA-Z0-9_-]+$", self.output_dataset_name):
            raise ValueError("output_dataset_name is not safe")

        return self


class MLInferenceModelSourceConfig(BaseModel):
    require_training_registry: bool = True
    require_model_card: bool = True
    require_artifact_metadata: bool = True
    require_artifact_hash: bool = True
    require_dataset_manifest_link: bool = True
    require_feature_columns_hash: bool = True
    allow_untrusted_artifact_load: bool = False
    allow_registry_external_paths: bool = False
    allow_manual_artifact_path: bool = False
    trusted_artifact_only: bool = True
    verify_artifact_hash_before_load: bool = True
    verify_environment_metadata: bool = True
    warn_environment_mismatch: bool = True
    block_environment_mismatch: bool = False

class MLInferenceDatasetConfig(BaseModel):
    require_ml_dataset_manifest: bool = True
    require_leakage_free_dataset: bool = True
    require_quality_passed_dataset: bool = True
    use_latest_dataset_if_not_specified: bool = True
    allow_inference_on_train_split: bool = True
    allow_inference_on_validation_split: bool = True
    allow_inference_on_test_split: bool = True
    allow_inference_on_new_offline_dataset: bool = True
    new_offline_dataset_requires_schema_match: bool = True
    reject_if_feature_contains_label: bool = True
    reject_if_feature_contains_future: bool = True
    reject_if_feature_contains_target: bool = True
    reject_if_feature_contains_order_execution: bool = True

class MLInferenceFeatureSchemaConfig(BaseModel):
    require_exact_feature_columns: bool = True
    require_exact_feature_order: bool = True
    allow_missing_features: bool = False
    allow_extra_features: bool = False
    allow_dtype_cast_numeric: bool = True
    reject_object_features: bool = True
    reject_nan_inf_features: bool = True
    max_nan_ratio_per_feature: float = 0.0
    feature_schema_hash_required: bool = True

class MLInferencePreprocessingConfig(BaseModel):
    transform_only: bool = True
    fit_forbidden: bool = True
    require_training_preprocessor_metadata: bool = True
    require_preprocessor_hash: bool = True
    allow_refit: bool = False
    allow_validation_fit: bool = False
    allow_test_fit: bool = False
    allow_inference_fit: bool = False
    imputer_transform_only: bool = True
    scaler_transform_only: bool = True
    clipper_transform_only: bool = True

class MLInferencePredictionConfig(BaseModel):
    mode: str = "offline_batch"
    allowed_modes: list[str] = Field(default_factory=lambda: ["offline_batch"])
    max_rows_per_batch: int = 100000
    batch_size: int = 10000
    deterministic: bool = True
    random_seed: int = 42
    require_predict_output: bool = True
    require_predict_proba_if_classifier_supports: bool = True
    allow_decision_function: bool = True
    store_raw_predictions: bool = True
    store_probabilities: bool = True
    store_confidence: bool = True
    prediction_intent: str = "research_only"
    output_trade_signal_forbidden: bool = True
    output_order_intent_forbidden: bool = True

class MLInferenceProbabilityConfig(BaseModel):
    enabled: bool = True
    require_probability_metadata: bool = True
    calibrated_probability_preferred: bool = True
    allow_uncalibrated_probability: bool = True
    warn_uncalibrated_probability: bool = True
    min_probability: float = 0.0
    max_probability: float = 1.0
    reject_probability_out_of_range: bool = True
    normalize_probability_rows: bool = False
    reject_probability_sum_invalid: bool = True
    probability_sum_tolerance: float = 0.000001

class MLInferenceCalibrationCheckConfig(BaseModel):
    enabled: bool = True
    compute_brier_score_if_labels_available: bool = True
    compute_ece_if_labels_available: bool = True
    compute_reliability_bins_if_labels_available: bool = True
    reliability_bins: int = 10
    require_label_for_calibration_metrics: bool = False
    warn_if_labels_missing: bool = True
    compare_to_training_calibration_report: bool = True
    max_brier_degradation_warning: float = 0.05
    max_ece_warning: float = 0.10

class MLInferenceThresholdSweepConfig(BaseModel):
    enabled: bool = True
    research_only: bool = True
    thresholds: list[float] = Field(default_factory=lambda: [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80])
    compute_precision_recall_by_threshold: bool = True
    compute_prediction_count_by_threshold: bool = True
    compute_coverage_by_threshold: bool = True
    execution_threshold_forbidden: bool = True
    auto_apply_threshold_forbidden: bool = True

class MLInferenceDistributionConfig(BaseModel):
    enabled: bool = True
    analyze_prediction_distribution: bool = True
    analyze_probability_distribution: bool = True
    analyze_confidence_buckets: bool = True
    analyze_class_distribution: bool = True
    confidence_buckets: list[list[float]] = Field(default_factory=lambda: [[0.0, 0.5], [0.5, 0.6], [0.6, 0.7], [0.7, 0.8], [0.8, 0.9], [0.9, 1.0]])
    warn_single_class_prediction_ratio: float = 0.90
    warn_low_confidence_mean: float = 0.55
    warn_probability_collapse: bool = True

class MLInferenceDriftConfig(BaseModel):
    enabled: bool = True
    skeleton_only: bool = True
    compare_to_training_feature_stats: bool = True
    compute_basic_feature_shift: bool = True
    compute_prediction_shift: bool = True
    compute_population_stability_index_skeleton: bool = True
    warn_high_feature_shift: bool = True
    warn_high_prediction_shift: bool = True
    drift_threshold_warning: float = 0.25
    production_drift_monitoring_deferred: bool = True

class MLInferenceSandboxIntegrationConfig(BaseModel):
    enabled: bool = True
    create_ml_signal_candidate_sandbox: bool = True
    create_ml_risk_context_sandbox: bool = True
    write_to_signal_engine_forbidden: bool = True
    write_to_risk_engine_forbidden: bool = True
    write_to_strategy_engine_forbidden: bool = True
    write_to_paper_engine_forbidden: bool = True
    write_to_live_engine_forbidden: bool = True
    require_integration_contract: bool = True
    require_no_order_intent: bool = True
    require_research_only_intent: bool = True

class MLInferenceQualityConfig(BaseModel):
    reject_no_model_loaded: bool = True
    reject_untrusted_artifact: bool = True
    reject_hash_mismatch: bool = True
    reject_schema_mismatch: bool = True
    reject_missing_model_card: bool = True
    reject_missing_dataset_manifest: bool = True
    reject_missing_predictions: bool = True
    reject_probability_out_of_range: bool = True
    reject_probability_sum_invalid: bool = True
    reject_nan_inf_outputs: bool = True
    reject_missing_inference_manifest: bool = True
    reject_missing_hashes: bool = True
    warn_uncalibrated_probability: bool = True
    warn_labels_missing_for_calibration_check: bool = True
    warn_prediction_single_class_collapse: bool = True
    warn_low_confidence: bool = True
    warn_feature_drift: bool = True
    reject_live_or_paper_intent: bool = True

class MLInferenceConfig(BaseModel):
    enabled: bool = True
    output_dataset_name: str = "ml_inference_runs"
    cache_enabled: bool = True
    cache_dir: str = "data/ml/inference/cache"
    export_dir: str = "data/ml/inference/exports"
    reports_dir: str = "data/ml/inference/reports"
    registry_dir: str = "data/ml/inference/registry"

    real_exchange_forbidden: bool = True
    paper_trade_forbidden: bool = True
    live_trade_forbidden: bool = True
    order_creation_forbidden: bool = True
    api_key_forbidden: bool = True
    signed_request_forbidden: bool = True
    dashboard_forbidden: bool = True
    prediction_serving_forbidden: bool = True
    online_inference_forbidden: bool = True
    execution_integration_forbidden: bool = True
    signal_auto_write_forbidden: bool = True
    risk_auto_write_forbidden: bool = True
    auto_strategy_update_forbidden: bool = True
    auto_model_promotion_forbidden: bool = True

    model_source: MLInferenceModelSourceConfig = Field(default_factory=MLInferenceModelSourceConfig)
    dataset: MLInferenceDatasetConfig = Field(default_factory=MLInferenceDatasetConfig)
    feature_schema: MLInferenceFeatureSchemaConfig = Field(default_factory=MLInferenceFeatureSchemaConfig)
    preprocessing: MLInferencePreprocessingConfig = Field(default_factory=MLInferencePreprocessingConfig)
    prediction: MLInferencePredictionConfig = Field(default_factory=MLInferencePredictionConfig)
    probability: MLInferenceProbabilityConfig = Field(default_factory=MLInferenceProbabilityConfig)
    calibration_check: MLInferenceCalibrationCheckConfig = Field(default_factory=MLInferenceCalibrationCheckConfig)
    threshold_sweep: MLInferenceThresholdSweepConfig = Field(default_factory=MLInferenceThresholdSweepConfig)
    distribution: MLInferenceDistributionConfig = Field(default_factory=MLInferenceDistributionConfig)
    drift: MLInferenceDriftConfig = Field(default_factory=MLInferenceDriftConfig)
    sandbox_integration: MLInferenceSandboxIntegrationConfig = Field(default_factory=MLInferenceSandboxIntegrationConfig)
    quality: MLInferenceQualityConfig = Field(default_factory=MLInferenceQualityConfig)

    @model_validator(mode="after")
    def validate_safety_flags(self) -> "MLInferenceConfig":
        if not self.real_exchange_forbidden: raise ValueError("real_exchange_forbidden must be True")
        if not self.paper_trade_forbidden: raise ValueError("paper_trade_forbidden must be True")
        if not self.live_trade_forbidden: raise ValueError("live_trade_forbidden must be True")
        if not self.order_creation_forbidden: raise ValueError("order_creation_forbidden must be True")
        if not self.api_key_forbidden: raise ValueError("api_key_forbidden must be True")
        if not self.signed_request_forbidden: raise ValueError("signed_request_forbidden must be True")
        if not self.dashboard_forbidden: raise ValueError("dashboard_forbidden must be True")
        if not self.prediction_serving_forbidden: raise ValueError("prediction_serving_forbidden must be True")
        if not self.online_inference_forbidden: raise ValueError("online_inference_forbidden must be True")
        if not self.execution_integration_forbidden: raise ValueError("execution_integration_forbidden must be True")
        if not self.signal_auto_write_forbidden: raise ValueError("signal_auto_write_forbidden must be True")
        if not self.risk_auto_write_forbidden: raise ValueError("risk_auto_write_forbidden must be True")
        if not self.auto_strategy_update_forbidden: raise ValueError("auto_strategy_update_forbidden must be True")
        if not self.auto_model_promotion_forbidden: raise ValueError("auto_model_promotion_forbidden must be True")

        if self.model_source.allow_untrusted_artifact_load: raise ValueError("allow_untrusted_artifact_load must be False")
        if self.model_source.allow_manual_artifact_path: raise ValueError("allow_manual_artifact_path must be False")
        if not self.model_source.trusted_artifact_only: raise ValueError("trusted_artifact_only must be True")
        if not self.model_source.verify_artifact_hash_before_load: raise ValueError("verify_artifact_hash_before_load must be True")

        if not self.feature_schema.require_exact_feature_columns: raise ValueError("require_exact_feature_columns must be True")
        if not self.feature_schema.require_exact_feature_order: raise ValueError("require_exact_feature_order must be True")
        if self.feature_schema.allow_missing_features: raise ValueError("allow_missing_features must be False")
        if self.feature_schema.allow_extra_features: raise ValueError("allow_extra_features must be False")

        if not self.preprocessing.transform_only: raise ValueError("transform_only must be True")
        if not self.preprocessing.fit_forbidden: raise ValueError("fit_forbidden must be True")
        if self.preprocessing.allow_refit: raise ValueError("allow_refit must be False")

        if self.prediction.mode != "offline_batch": raise ValueError("prediction mode must be offline_batch")
        if self.prediction.prediction_intent not in ("research_only", "no_order", "validation_only", "no_live", "no_paper"): raise ValueError("prediction_intent must be research_only or no_order")
        if not self.prediction.output_trade_signal_forbidden: raise ValueError("output_trade_signal_forbidden must be True")
        if not self.prediction.output_order_intent_forbidden: raise ValueError("output_order_intent_forbidden must be True")

        if self.probability.min_probability < 0.0 or self.probability.max_probability > 1.0: raise ValueError("probability min/max must be between 0 and 1")
        if self.calibration_check.reliability_bins < 2 or self.calibration_check.reliability_bins > 50: raise ValueError("reliability_bins must be between 2 and 50")
        if any(t < 0.0 or t > 1.0 for t in self.threshold_sweep.thresholds): raise ValueError("threshold values must be between 0 and 1")

        if not self.threshold_sweep.execution_threshold_forbidden: raise ValueError("execution_threshold_forbidden must be True")
        if not self.threshold_sweep.auto_apply_threshold_forbidden: raise ValueError("auto_apply_threshold_forbidden must be True")

        if not self.sandbox_integration.write_to_signal_engine_forbidden: raise ValueError("write_to_signal_engine_forbidden must be True")
        if not self.sandbox_integration.write_to_risk_engine_forbidden: raise ValueError("write_to_risk_engine_forbidden must be True")
        if not self.sandbox_integration.write_to_strategy_engine_forbidden: raise ValueError("write_to_strategy_engine_forbidden must be True")
        if not self.sandbox_integration.write_to_paper_engine_forbidden: raise ValueError("write_to_paper_engine_forbidden must be True")
        if not self.sandbox_integration.write_to_live_engine_forbidden: raise ValueError("write_to_live_engine_forbidden must be True")

        if not re.match(r"^[a-zA-Z0-9_-]+$", self.output_dataset_name): raise ValueError("output_dataset_name is not safe")

        return self



class PortfolioSandboxInputConfig(BaseModel):
    use_scored_signals: bool = True
    use_risk_assessments: bool = True
    use_ml_blended_candidates: bool = True
    use_regime_context: bool = True
    require_at_least_one_candidate_source: bool = True
    require_risk_context: bool = False
    require_ml_blend_context: bool = False
    allow_missing_ml_with_penalty: bool = True
    allow_missing_risk_with_penalty: bool = True
    reject_execution_fields: bool = True
    reject_live_paper_intent: bool = True

class PortfolioCandidateNormalizationConfig(BaseModel):
    score_min: float = 0.0
    score_max: float = 100.0
    probability_min: float = 0.0
    probability_max: float = 1.0
    normalize_ml_probability_to_score: bool = True
    normalize_signal_score: bool = True
    normalize_risk_score: bool = True
    require_explanation: bool = True
    require_source_trace: bool = True

class PortfolioEligibilityConfig(BaseModel):
    enabled: bool = True
    min_signal_score: float = 60.0
    min_risk_score: float = 50.0
    min_ml_blend_score: float = 50.0
    allow_research_only_candidates: bool = True
    reject_blocked_risk: bool = True
    reject_missing_symbol: bool = True
    reject_missing_interval: bool = True
    reject_missing_direction: bool = True
    reject_stale_candidates: bool = True
    max_candidate_age_bars: int = 3
    reject_duplicate_symbol_direction_bar: bool = True

class PortfolioCorrelationConfig(BaseModel):
    enabled: bool = True
    method: str = "pearson"
    allowed_methods: list[str] = Field(default_factory=lambda: ["pearson", "spearman", "kendall"])
    lookback_bars: int = 500
    min_periods: int = 100
    use_returns: bool = True
    return_column: str = "close"
    reject_forward_returns: bool = True
    reject_future_columns: bool = True
    max_abs_pair_correlation_warning: float = 0.80
    max_abs_pair_correlation_block: float = 0.95
    missing_correlation_policy: str = "penalty"
    correlation_penalty: float = 15.0

    @model_validator(mode="after")
    def validate_correlation_config(self) -> "PortfolioCorrelationConfig":
        if self.lookback_bars <= self.min_periods:
            raise ValueError("lookback_bars must be greater than min_periods")
        if self.max_abs_pair_correlation_block < self.max_abs_pair_correlation_warning:
            raise ValueError("block threshold cannot be lower than warning threshold")
        return self

class PortfolioSimilarityConfig(BaseModel):
    enabled: bool = True
    use_cosine_similarity_for_candidate_vectors: bool = True
    similarity_threshold_warning: float = 0.85
    similarity_threshold_block: float = 0.95
    include_score_vector: list[str] = Field(default_factory=lambda: [
        "signal_score", "risk_score", "ml_blend_score", "regime_score", "volatility_risk", "liquidity_risk"
    ])
    missing_vector_policy: str = "warning"

class PortfolioExposureConfig(BaseModel):
    enabled: bool = True
    mode: str = "hypothetical_only"
    starting_equity_usdt: float = 1000.0
    max_total_hypothetical_exposure_pct: float = 30.0
    max_symbol_hypothetical_exposure_pct: float = 10.0
    max_directional_exposure_pct: float = 20.0
    max_candidates_selected: int = 5
    max_candidates_per_symbol: int = 1
    max_candidates_per_interval: int = 5
    max_candidates_same_direction: int = 4
    default_candidate_notional_usdt: float = 50.0
    use_risk_hypothetical_notional_if_available: bool = True
    real_balance_fetch_forbidden: bool = True

    @model_validator(mode="after")
    def validate_exposure_config(self) -> "PortfolioExposureConfig":
        if not (0.0 <= self.max_total_hypothetical_exposure_pct <= 100.0):
            raise ValueError("max_total_hypothetical_exposure_pct must be between 0 and 100")
        if not (0.0 <= self.max_symbol_hypothetical_exposure_pct <= 100.0):
            raise ValueError("max_symbol_hypothetical_exposure_pct must be between 0 and 100")
        if not (0.0 <= self.max_directional_exposure_pct <= 100.0):
            raise ValueError("max_directional_exposure_pct must be between 0 and 100")
        if self.max_candidates_selected < 1:
            raise ValueError("max_candidates_selected must be at least 1")
        return self

class PortfolioConcentrationConfig(BaseModel):
    enabled: bool = True
    max_single_symbol_weight_pct: float = 20.0
    max_top_3_symbol_weight_pct: float = 60.0
    max_same_regime_ratio: float = 0.80
    max_same_direction_ratio: float = 0.80
    max_same_strategy_plugin_ratio: float = 0.70
    concentration_penalty: float = 20.0
    warn_high_concentration: bool = True

    @model_validator(mode="after")
    def validate_concentration_config(self) -> "PortfolioConcentrationConfig":
        if not (0.0 <= self.max_same_regime_ratio <= 1.0):
            raise ValueError("max_same_regime_ratio must be between 0 and 1")
        if not (0.0 <= self.max_same_direction_ratio <= 1.0):
            raise ValueError("max_same_direction_ratio must be between 0 and 1")
        if not (0.0 <= self.max_same_strategy_plugin_ratio <= 1.0):
            raise ValueError("max_same_strategy_plugin_ratio must be between 0 and 1")
        return self

class PortfolioDiversificationConfig(BaseModel):
    enabled: bool = True
    reward_low_correlation: bool = True
    reward_signal_source_diversity: bool = True
    reward_regime_diversity: bool = True
    reward_interval_diversity: bool = False
    diversification_bonus_max: float = 10.0
    low_diversification_penalty: float = 15.0

class PortfolioRiskBudgetConfig(BaseModel):
    enabled: bool = True
    mode: str = "placeholder"
    max_total_risk_budget_pct: float = 2.0
    max_single_candidate_risk_budget_pct: float = 0.50
    risk_budget_unit: str = "percent_of_simulated_equity"
    allocate_budget_production_forbidden: bool = True
    budget_is_hypothetical: bool = True

class PortfolioRankingConfig(BaseModel):
    enabled: bool = True
    method: str = "weighted_score"
    score_clamp_min: float = 0.0
    score_clamp_max: float = 100.0
    components: dict[str, float] = Field(default_factory=lambda: {
        "candidate_quality_weight": 0.30,
        "risk_quality_weight": 0.20,
        "ml_blend_weight": 0.20,
        "diversification_weight": 0.10,
        "correlation_penalty_weight": -0.10,
        "concentration_penalty_weight": -0.10,
        "liquidity_penalty_weight": -0.05,
        "stale_candidate_penalty_weight": -0.05
    })
    require_breakdown: bool = True
    require_explanation: bool = True

class PortfolioOptimizerSkeletonConfig(BaseModel):
    enabled: bool = True
    default_enabled_for_selection: bool = False
    scipy_optional: bool = True
    fail_if_scipy_missing: bool = False
    method: str = "slsqp_skeleton"
    constraints: dict[str, bool | float] = Field(default_factory=lambda: {
        "sum_weights_lte_one": True,
        "long_only_weights": True,
        "max_single_weight": 0.20,
        "max_total_exposure": 0.30,
        "max_pair_correlation": 0.80
    })
    production_allocation_forbidden: bool = True
    optimization_output_sandbox_only: bool = True

    @model_validator(mode="after")
    def validate_optimizer_skeleton_config(self) -> "PortfolioOptimizerSkeletonConfig":
        if not self.production_allocation_forbidden:
            raise ValueError("production_allocation_forbidden must be True")
        return self

class PortfolioSandboxOutputConfig(BaseModel):
    create_selected_candidate_set: bool = True
    create_portfolio_selection_report: bool = True
    create_allocation_placeholder: bool = True
    selected_candidate_production_forbidden: bool = True
    allocation_production_forbidden: bool = True
    write_to_signal_engine_forbidden: bool = True
    write_to_risk_engine_forbidden: bool = True
    write_to_paper_engine_forbidden: bool = True
    write_to_live_engine_forbidden: bool = True
    require_blocked_flags: bool = True
    require_research_only_intent: bool = True
    require_no_order_intent: bool = True

class PortfolioSandboxQualityConfig(BaseModel):
    reject_no_candidates: bool = False
    warn_no_candidates: bool = True
    reject_missing_breakdown: bool = True
    reject_missing_explanation: bool = True
    reject_score_out_of_range: bool = True
    reject_nan_inf_scores: bool = True
    reject_missing_hashes: bool = True
    reject_forward_correlation: bool = True
    reject_future_columns: bool = True
    reject_production_write_intent: bool = True
    reject_live_or_paper_intent: bool = True
    warn_high_correlation: bool = True
    warn_high_concentration: bool = True
    warn_low_diversification: bool = True
    warn_missing_correlation_data: bool = True

class PortfolioSandboxConfig(BaseModel):
    enabled: bool = True
    output_dataset_name: str = "portfolio_candidate_selection_sandbox"
    cache_enabled: bool = True
    cache_dir: str = "data/portfolio/sandbox/cache"
    export_dir: str = "data/portfolio/sandbox/exports"
    reports_dir: str = "data/portfolio/sandbox/reports"

    real_exchange_forbidden: bool = True
    paper_trade_forbidden: bool = True
    live_trade_forbidden: bool = True
    order_creation_forbidden: bool = True
    api_key_forbidden: bool = True
    signed_request_forbidden: bool = True
    dashboard_forbidden: bool = True
    signal_auto_write_forbidden: bool = True
    risk_auto_write_forbidden: bool = True
    paper_auto_write_forbidden: bool = True
    live_auto_write_forbidden: bool = True
    allocation_production_forbidden: bool = True
    position_sizing_production_forbidden: bool = True

    inputs: PortfolioSandboxInputConfig = Field(default_factory=PortfolioSandboxInputConfig)
    candidate_normalization: PortfolioCandidateNormalizationConfig = Field(default_factory=PortfolioCandidateNormalizationConfig)
    eligibility: PortfolioEligibilityConfig = Field(default_factory=PortfolioEligibilityConfig)
    correlation: PortfolioCorrelationConfig = Field(default_factory=PortfolioCorrelationConfig)
    similarity: PortfolioSimilarityConfig = Field(default_factory=PortfolioSimilarityConfig)
    exposure: PortfolioExposureConfig = Field(default_factory=PortfolioExposureConfig)
    concentration: PortfolioConcentrationConfig = Field(default_factory=PortfolioConcentrationConfig)
    diversification: PortfolioDiversificationConfig = Field(default_factory=PortfolioDiversificationConfig)
    risk_budget: PortfolioRiskBudgetConfig = Field(default_factory=PortfolioRiskBudgetConfig)
    ranking: PortfolioRankingConfig = Field(default_factory=PortfolioRankingConfig)
    optimizer_skeleton: PortfolioOptimizerSkeletonConfig = Field(default_factory=PortfolioOptimizerSkeletonConfig)
    sandbox_output: PortfolioSandboxOutputConfig = Field(default_factory=PortfolioSandboxOutputConfig)
    quality: PortfolioSandboxQualityConfig = Field(default_factory=PortfolioSandboxQualityConfig)

    @model_validator(mode="after")
    def validate_safety_flags(self) -> "PortfolioSandboxConfig":
        if not self.real_exchange_forbidden: raise ValueError("real_exchange_forbidden must be True")
        if not self.paper_trade_forbidden: raise ValueError("paper_trade_forbidden must be True")
        if not self.live_trade_forbidden: raise ValueError("live_trade_forbidden must be True")
        if not self.order_creation_forbidden: raise ValueError("order_creation_forbidden must be True")
        if not self.api_key_forbidden: raise ValueError("api_key_forbidden must be True")
        if not self.signed_request_forbidden: raise ValueError("signed_request_forbidden must be True")
        if not self.dashboard_forbidden: raise ValueError("dashboard_forbidden must be True")
        if not self.signal_auto_write_forbidden: raise ValueError("signal_auto_write_forbidden must be True")
        if not self.risk_auto_write_forbidden: raise ValueError("risk_auto_write_forbidden must be True")
        if not self.paper_auto_write_forbidden: raise ValueError("paper_auto_write_forbidden must be True")
        if not self.live_auto_write_forbidden: raise ValueError("live_auto_write_forbidden must be True")
        if not self.allocation_production_forbidden: raise ValueError("allocation_production_forbidden must be True")
        if not self.position_sizing_production_forbidden: raise ValueError("position_sizing_production_forbidden must be True")

        import re
        if not re.match(r"^[a-zA-Z0-9_-]+$", self.output_dataset_name):
            raise ValueError("output_dataset_name is not safe")

        return self

class AppConfig(BaseModel):
    portfolio_sandbox: PortfolioSandboxConfig = Field(default_factory=PortfolioSandboxConfig)
    ml_dataset: MLDatasetConfig = Field(default_factory=MLDatasetConfig)
    ml_training: MLTrainingConfig = Field(default_factory=MLTrainingConfig)
    ml_inference: MLInferenceConfig = Field(default_factory=MLInferenceConfig)


    optimizer: OptimizerConfig = OptimizerConfig()
    walkforward: WalkForwardConfig = Field(default_factory=WalkForwardConfig)
    backtest_reporting: BacktestReportingConfig = BacktestReportingConfig()

    risk: RiskConfig = Field(default_factory=RiskConfig)
    paper: PaperConfig = Field(default_factory=PaperConfig)
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
    indicator_v2: IndicatorV2Config = Field(default_factory=IndicatorV2Config)
    market_data: MarketDataConfig = MarketDataConfig()
    streams: StreamsConfig = StreamsConfig()
    storage: StorageConfig = StorageConfig()
    indicators: IndicatorsConfig = Field(default_factory=IndicatorsConfig)
    strategies: StrategiesConfig = Field(default_factory=StrategiesConfig)
    signals: SignalsConfig = Field(default_factory=SignalsConfig)
    regimes: RegimesConfig = Field(default_factory=RegimesConfig)

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
