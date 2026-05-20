from binance50.config.models import AppConfig
from binance50.core.exceptions import ConfigValidationError, SafetyError
from binance50.network.clock import ClockSyncService


def assert_clock_config_safe(config: AppConfig) -> None:
    if config.binance_timing.recv_window_ms > config.binance_timing.recv_window_max_ms:
        raise ConfigValidationError("recv_window_ms exceeds maximum")
    if config.binance_timing.max_allowed_clock_drift_ms > 5000:
        raise SafetyError("max_allowed_clock_drift_ms is too high (should be <= 5000)")


def assert_signed_request_clock_safe(config: AppConfig, clock_service: ClockSyncService) -> None:
    clock_service.require_valid_clock_for_signed_request(config)


def build_clock_safety_report(
    config: AppConfig, clock_service: ClockSyncService | None = None
) -> dict:
    try:
        assert_clock_config_safe(config)
        config_safe = True
        reason = None
    except Exception as e:
        config_safe = False
        reason = str(e)

    drift_acceptable = True
    if clock_service:
        drift_acceptable = clock_service.is_drift_acceptable(config)

    return {
        "config_safe": config_safe,
        "config_error_reason": reason,
        "clock_sync_enabled": config.binance_timing.clock_sync_enabled,
        "drift_acceptable": drift_acceptable,
        "drift_ms": clock_service.get_current_offset_ms() if clock_service else None,
    }
