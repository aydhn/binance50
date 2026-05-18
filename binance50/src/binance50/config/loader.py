import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

from binance50.config.models import AppConfig
from binance50.core.exceptions import ConfigError


def load_config(config_dir: str = "config") -> AppConfig:
    load_dotenv()

    config_path = Path(config_dir) / "default.yaml"
    environments_path = Path(config_dir) / "environments.yaml"

    if not config_path.exists():
        raise ConfigError(f"Config file not found: {config_path}")

    try:
        with open(config_path, encoding="utf-8") as f:
            config_data = yaml.safe_load(f) or {}

        if environments_path.exists():
            with open(environments_path, encoding="utf-8") as f:
                environments_data = yaml.safe_load(f) or {}
            config_data["environment_matrix"] = environments_data

        # Environment overrides
        if "BINANCE50_ENVIRONMENT_PROFILE" in os.environ:
            if "runtime" not in config_data:
                config_data["runtime"] = {}
            env_profile = os.environ["BINANCE50_ENVIRONMENT_PROFILE"]
            config_data["runtime"]["environment_profile"] = env_profile

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

        if "BINANCE50_ACCOUNT_DOMAIN" in os.environ:
            if "runtime" not in config_data:
                config_data["runtime"] = {}
            config_data["runtime"]["account_domain"] = os.environ["BINANCE50_ACCOUNT_DOMAIN"]

        if "BINANCE50_CONNECTION_ENABLED" in os.environ:
            if "connector" not in config_data:
                config_data["connector"] = {}
            val = os.environ["BINANCE50_CONNECTION_ENABLED"].lower() in ("true", "1", "yes")
            config_data["connector"]["connection_enabled"] = val

        if "BINANCE50_WEBSOCKET_ENABLED" in os.environ:
            if "connector" not in config_data:
                config_data["connector"] = {}
            val = os.environ["BINANCE50_WEBSOCKET_ENABLED"].lower() in ("true", "1", "yes")
            config_data["connector"]["websocket_enabled"] = val

        if "BINANCE50_ORDER_GATEWAY_ENABLED" in os.environ:
            if "connector" not in config_data:
                config_data["connector"] = {}
            val = os.environ["BINANCE50_ORDER_GATEWAY_ENABLED"].lower() in ("true", "1", "yes")
            config_data["connector"]["order_gateway_enabled"] = val

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

        app_config = AppConfig(**config_data)

        # Check if the profile resolves correctly to trigger validation errors
        _ = app_config.selected_environment_profile

        return app_config

    except Exception as e:
        raise ConfigError(f"Failed to load config: {str(e)}") from e
