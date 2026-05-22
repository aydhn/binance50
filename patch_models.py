import re

with open("binance50/src/binance50/config/models.py", "r") as f:
    content = f.read()

# Check if StreamsConfig already exists to avoid duplicate logic
if "StreamsConfig" not in content:
    models_import_code = """
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
"""
    # Insert it before AppConfig
    content = content.replace("class AppConfig(BaseModel):", models_import_code + "\nclass AppConfig(BaseModel):")

    # Add streams to AppConfig
    content = content.replace("market_data: MarketDataConfig = MarketDataConfig()", "market_data: MarketDataConfig = MarketDataConfig()\n    streams: StreamsConfig = StreamsConfig()")

    with open("binance50/src/binance50/config/models.py", "w") as f:
        f.write(content)
