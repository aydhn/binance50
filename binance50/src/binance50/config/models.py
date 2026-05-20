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


class AppConfig(BaseModel):
    project: ProjectConfig = ProjectConfig()
    runtime: RuntimeConfig = RuntimeConfig()
    safety: SafetyConfig = SafetyConfig()
    credentials: CredentialsConfig = CredentialsConfig()
    logging: LoggingConfig = LoggingConfig()
    data: DataConfig = DataConfig()
    reports: ReportsConfig = ReportsConfig()
    connector: ConnectorConfig = ConnectorConfig()
    environment_matrix: EnvironmentMatrixConfig = EnvironmentMatrixConfig()

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
