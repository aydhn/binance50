import logging

from binance50.audit.writer import audit_event
from binance50.config.loader import load_config
from binance50.core.exception_handler import handle_exception
from binance50.logging.context import set_correlation_id, set_runtime_context
from binance50.logging.setup import setup_logging
from binance50.safety.live_guard import check_live_trading_guard
from binance50.safety.mode_guard import check_mode_consistency
from binance50.safety.secrets_guard import check_for_leaked_secrets


def init_app() -> None:
    """Initialize application."""
    set_correlation_id()

    # 1. Setup logging first
    try:
        setup_logging()
    except Exception as e:
        print(f"CRITICAL: Could not setup logging: {e}")
        return

    logger = logging.getLogger("binance50.app")

    try:
        # 2. Load config
        logger.info("Loading configuration...")
        config = load_config()

        # Set runtime context
        set_runtime_context(
            environment_profile=config.selected_environment_profile.profile_name.value,
            trading_mode=config.runtime.trading_mode.value,
            market_scope=config.runtime.market_scope.value,
            app_version="0.1.0",
        )

        audit_event("app_start", "app", "initialize")
        audit_event("config_loaded", "app", "load_config")

        # 3. Run safety checks
        logger.info("Running safety checks...")
        audit_event("safety_check_started", "app", "safety_check")

        warnings = check_for_leaked_secrets()
        for w in warnings:
            logger.warning(w)

        check_mode_consistency(config)
        check_live_trading_guard(config)

        audit_event("safety_check_passed", "app", "safety_check")

        logger.info("binance50 foundation ready.")
        logger.info(f"Trading Mode: {config.runtime.trading_mode.value}")
        logger.info(f"Environment: {config.selected_environment_profile.profile_name.value}")

        audit_event(
            "connector_disabled",
            "app",
            "connector_initialization",
            message="Connector is disabled in Phase 3",
        )

    except Exception as e:
        audit_event("safety_check_failed", "app", "safety_check", status="failed", message=str(e))
        handle_exception(e, component="app", action="init_app", logger=logger)
        audit_event("app_stop", "app", "shutdown", status="failed")
        raise

    audit_event("app_stop", "app", "shutdown")


if __name__ == "__main__":
    init_app()
