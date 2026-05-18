import logging

from binance50.config.loader import load_config
from binance50.logging.setup import setup_logging
from binance50.safety.live_guard import check_live_trading_guard
from binance50.safety.mode_guard import check_mode_consistency
from binance50.safety.secrets_guard import check_for_leaked_secrets

logger = logging.getLogger("binance50.app")


def init_app() -> None:
    """Initialize application."""
    # 1. Setup logging first
    setup_logging()

    # 2. Load config
    logger.info("Loading configuration...")
    config = load_config()

    # 3. Run safety checks
    logger.info("Running safety checks...")

    warnings = check_for_leaked_secrets()
    for w in warnings:
        logger.warning(w)

    check_mode_consistency(config)
    check_live_trading_guard(config)

    logger.info("binance50 foundation ready.")
    logger.info(f"Trading Mode: {config.runtime.trading_mode.value}")
    logger.info(f"Environment: {config.runtime.environment.value}")


if __name__ == "__main__":
    init_app()
