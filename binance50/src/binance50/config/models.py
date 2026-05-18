from pydantic import BaseModel, Field, model_validator

from binance50.core.enums import MarketScope, RuntimeEnvironment, TradingMode


class ProjectConfig(BaseModel):
    name: str = "binance50"
    version: str = "0.1.0"


class RuntimeConfig(BaseModel):
    environment: RuntimeEnvironment = RuntimeEnvironment.LOCAL
    trading_mode: TradingMode = TradingMode.PAPER
    market_scope: MarketScope = MarketScope.SPOT
    timezone: str = "UTC"


class SafetyConfig(BaseModel):
    enable_live_trading: bool = False
    confirm_live_trading: bool = False
    max_symbols_initial: int = Field(default=5, ge=1, le=20)
    default_quote_asset: str = "USDT"

    @model_validator(mode="after")
    def validate_quote_asset(self) -> "SafetyConfig":
        if not self.default_quote_asset:
            raise ValueError("Quote asset cannot be empty")
        return self


class LoggingConfig(BaseModel):
    level: str = "INFO"
    log_dir: str = "logs"


class DataConfig(BaseModel):
    root_dir: str = "data"


class ReportsConfig(BaseModel):
    root_dir: str = "reports"


class AppConfig(BaseModel):
    project: ProjectConfig = ProjectConfig()
    runtime: RuntimeConfig = RuntimeConfig()
    safety: SafetyConfig = SafetyConfig()
    logging: LoggingConfig = LoggingConfig()
    data: DataConfig = DataConfig()
    reports: ReportsConfig = ReportsConfig()

    @model_validator(mode="after")
    def validate_live_trading(self) -> "AppConfig":
        if self.runtime.trading_mode == TradingMode.LIVE:
            if not self.safety.enable_live_trading or not self.safety.confirm_live_trading:
                raise ValueError(
                    "Live trading requires enable_live_trading and confirm_live_trading to be true"
                )
        return self
