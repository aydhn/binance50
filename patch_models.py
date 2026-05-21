import re
from pathlib import Path

models_path = Path("binance50/src/binance50/config/models.py")
with open(models_path, "r") as f:
    content = f.read()

market_data_models = """
from typing import Literal

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
            raise ConfigValidationError("real_fetch_enabled=True is blocked in Phase 8 default safety")
        for inv in self.default_intervals:
            if inv not in self.allowed_intervals:
                raise ValueError(f"default_interval {inv} must be in allowed_intervals")
        for inv in self.default_intervals:
            if inv not in self.default_history_days:
                raise ValueError(f"default_history_days must cover {inv}")
        return self

"""

app_config_pattern = r"class AppConfig\(BaseModel\):(.*?)universe: UniverseConfig = UniverseConfig\(\)"
app_config_replacement = r"""class AppConfig(BaseModel):\1universe: UniverseConfig = UniverseConfig()
    market_data: MarketDataConfig = MarketDataConfig()"""

if "MarketDataConfig" not in content:
    # Find insertion point before AppConfig
    app_config_idx = content.find("class AppConfig(BaseModel):")
    if app_config_idx != -1:
        new_content = content[:app_config_idx] + market_data_models + content[app_config_idx:]
        new_content = re.sub(app_config_pattern, app_config_replacement, new_content, flags=re.DOTALL)

        # Also need to make sure Literal is imported
        if "from typing import Literal" not in new_content:
            new_content = new_content.replace("from typing import Any, Optional", "from typing import Any, Optional, Literal")

        with open(models_path, "w") as f:
            f.write(new_content)
        print("Updated models.py")
    else:
        print("Could not find AppConfig in models.py")
else:
    print("MarketDataConfig already exists in models.py")
