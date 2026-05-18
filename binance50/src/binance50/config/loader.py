import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

from binance50.config.models import AppConfig
from binance50.core.exceptions import ConfigError


def load_config(config_dir: str = "config") -> AppConfig:
    load_dotenv()

    config_path = Path(config_dir) / "default.yaml"
    if not config_path.exists():
        raise ConfigError(f"Config file not found: {config_path}")

    try:
        with open(config_path, encoding="utf-8") as f:
            config_data = yaml.safe_load(f) or {}

        # Environment overrides
        if "BINANCE50_ENV" in os.environ:
            if "runtime" not in config_data:
                config_data["runtime"] = {}
            config_data["runtime"]["environment"] = os.environ["BINANCE50_ENV"]

        if "BINANCE50_TRADING_MODE" in os.environ:
            if "runtime" not in config_data:
                config_data["runtime"] = {}
            config_data["runtime"]["trading_mode"] = os.environ["BINANCE50_TRADING_MODE"]

        if "BINANCE50_MARKET_SCOPE" in os.environ:
            if "runtime" not in config_data:
                config_data["runtime"] = {}
            config_data["runtime"]["market_scope"] = os.environ["BINANCE50_MARKET_SCOPE"]

        if "BINANCE50_ENABLE_LIVE_TRADING" in os.environ:
            if "safety" not in config_data:
                config_data["safety"] = {}
            val = os.environ["BINANCE50_ENABLE_LIVE_TRADING"].lower() in ("true", "1", "yes")
            config_data["safety"]["enable_live_trading"] = val

        if "BINANCE50_CONFIRM_LIVE_TRADING" in os.environ:
            if "safety" not in config_data:
                config_data["safety"] = {}
            val = os.environ["BINANCE50_CONFIRM_LIVE_TRADING"].lower() in ("true", "1", "yes")
            config_data["safety"]["confirm_live_trading"] = val

        if "BINANCE50_EXCHANGE" in os.environ:
            exc = os.environ["BINANCE50_EXCHANGE"].lower()
            if exc != "binance":
                raise ConfigError(f"Unsupported exchange: {exc}. Only binance is supported.")

        return AppConfig(**config_data)

    except Exception as e:
        raise ConfigError(f"Failed to load config: {str(e)}") from e
