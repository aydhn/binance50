import re
from pathlib import Path

file_path = Path("src/binance50/config/models.py")
content = file_path.read_text()

imports = """
from typing import Any, Literal
"""

if "from typing import Any" not in content:
    content = content.replace("from typing import", "from typing import Any, Literal,")

indicator_config_classes = """
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
    allowed_backends: list[str] = Field(default_factory=lambda: ["native", "talib_optional", "pandas_ta_optional"])
    fail_if_optional_backend_missing: bool = False
    input_source_priority: list[str] = Field(default_factory=lambda: ["warehouse", "market_data_cache", "fixture"])
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
    default_periods: dict[str, int] = Field(default_factory=lambda: {
        "short": 9,
        "medium": 14,
        "long": 21,
        "slow": 50,
        "very_slow": 200
    })
    trend: IndicatorTrendConfig = Field(default_factory=IndicatorTrendConfig)
    momentum: IndicatorMomentumConfig = Field(default_factory=IndicatorMomentumConfig)
    volatility: IndicatorVolatilityConfig = Field(default_factory=IndicatorVolatilityConfig)
    volume: IndicatorVolumeConfig = Field(default_factory=IndicatorVolumeConfig)
    transforms: IndicatorTransformsConfig = Field(default_factory=IndicatorTransformsConfig)
    quality: IndicatorQualityConfig = Field(default_factory=IndicatorQualityConfig)

"""

if "class IndicatorsConfig" not in content:
    content = content.replace("class AppConfig(BaseModel):", indicator_config_classes + "\nclass AppConfig(BaseModel):")

    # Add indicators to AppConfig
    app_config_pattern = r"class AppConfig\(BaseModel\):.*?(?=\n\n|\Z)"

    content = re.sub(
        r"(class AppConfig\(BaseModel\):.*?)(\n[ \t]*def )",
        r"\1\n    indicators: IndicatorsConfig = Field(default_factory=IndicatorsConfig)\2",
        content,
        flags=re.DOTALL
    )

file_path.write_text(content)
print("Patched config models")
