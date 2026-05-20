from binance50.config.models import AppConfig
from binance50.core.exceptions import ConfigValidationError, SafetyError
from binance50.rate_limit.limiter import RateLimiter


def assert_rate_limit_config_safe(config: AppConfig) -> None:
    if config.network.retry_on_418:
        raise SafetyError("retry_on_418 must be False for safety")
    if config.network.retry_on_429:
        raise SafetyError("retry_on_429 should usually be False to use cooldown logic")
    if (
        config.rate_limit.safety_usage_threshold_pct
        >= config.rate_limit.critical_usage_threshold_pct
    ):
        raise ConfigValidationError("safety usage threshold must be less than critical threshold")


def assert_not_in_hard_cooldown(limiter: RateLimiter) -> None:
    if limiter.is_in_cooldown() and limiter.cooldown._is_hard_stop:
        raise SafetyError(f"Currently in hard cooldown: {limiter.cooldown.get_reason()}")


def validate_websocket_limits_safe(config: AppConfig) -> None:
    if config.websocket_limits.spot_max_incoming_messages_per_second > 5:
        raise SafetyError("Spot WebSocket max incoming messages cannot exceed 5/s")
    if config.websocket_limits.usdm_max_incoming_messages_per_second > 10:
        raise SafetyError("USDⓈ-M WebSocket max incoming messages cannot exceed 10/s")
    if config.websocket_limits.spot_max_streams_per_connection > 1024:
        raise SafetyError("Spot WebSocket max streams cannot exceed 1024")
    if config.websocket_limits.usdm_max_streams_per_connection > 200:
        raise SafetyError("USDⓈ-M WebSocket max streams cannot exceed 200")


def build_rate_limit_safety_report(config: AppConfig, limiter: RateLimiter | None = None) -> dict:
    try:
        assert_rate_limit_config_safe(config)
        validate_websocket_limits_safe(config)
        config_safe = True
        reason = None
    except Exception as e:
        config_safe = False
        reason = str(e)

    hard_cooldown = False
    if limiter and limiter.is_in_cooldown() and limiter.cooldown._is_hard_stop:
        hard_cooldown = True

    return {
        "config_safe": config_safe,
        "config_error_reason": reason,
        "hard_cooldown_active": hard_cooldown,
    }
