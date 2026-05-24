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
    def validate_use_centered_window(cls, v: bool) -> bool:
        if v:
            raise ValueError("use_centered_window must be False in Phase 12")
        return v

    @field_validator("allow_repainting")
    def validate_allow_repainting(cls, v: bool) -> bool:
        if v:
            raise ValueError("allow_repainting must be False in Phase 12")
        return v

    @field_validator("confirm_after_bars")
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
    def validate_disallow_forward(cls, v: bool) -> bool:
        if not v:
            raise ValueError("disallow_forward_alignment must be True")
        return v

    @field_validator("disallow_nearest_alignment")
    def validate_disallow_nearest(cls, v: bool) -> bool:
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
    def validate_actionable_language(cls, v: bool) -> bool:
        if v:
            raise ValueError("allow_actionable_order_language must be False in Phase 13")
        return v

    @field_validator("require_non_order_intent")
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
    def validate_forbidden(cls, v: bool, info) -> bool:
        if not v:
            raise ValueError(f"{info.field_name} must be True in Phase 14")
        return v

    @field_validator("plugin_weights")
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
