import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

from binance50.config.models import AppConfig
from binance50.core.exceptions import ConfigError


def _parse_bool(value: str) -> bool:
    if value is None:
        return False
    value_lower = value.lower().strip()
    if value_lower in ("true", "1", "yes", "y", "on"):
        return True
    elif value_lower in ("false", "0", "no", "n", "off"):
        return False
    else:
        raise ConfigError(f"Invalid boolean value: {value}")


def _parse_ip_list(value: str) -> list[str]:
    if not value or not value.strip():
        return []
    return [ip.strip() for ip in value.split(",") if ip.strip()]


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
            config_data["connector"]["connection_enabled"] = _parse_bool(
                os.environ["BINANCE50_CONNECTION_ENABLED"]
            )

        if "BINANCE50_WEBSOCKET_ENABLED" in os.environ:
            if "connector" not in config_data:
                config_data["connector"] = {}
            config_data["connector"]["websocket_enabled"] = _parse_bool(
                os.environ["BINANCE50_WEBSOCKET_ENABLED"]
            )

        if "BINANCE50_ORDER_GATEWAY_ENABLED" in os.environ:
            if "connector" not in config_data:
                config_data["connector"] = {}
            config_data["connector"]["order_gateway_enabled"] = _parse_bool(
                os.environ["BINANCE50_ORDER_GATEWAY_ENABLED"]
            )

        if "BINANCE50_ENABLE_LIVE_TRADING" in os.environ:
            if "safety" not in config_data:
                config_data["safety"] = {}
            config_data["safety"]["enable_live_trading"] = _parse_bool(
                os.environ["BINANCE50_ENABLE_LIVE_TRADING"]
            )

        if "BINANCE50_CONFIRM_LIVE_TRADING" in os.environ:
            if "safety" not in config_data:
                config_data["safety"] = {}
            config_data["safety"]["confirm_live_trading"] = _parse_bool(
                os.environ["BINANCE50_CONFIRM_LIVE_TRADING"]
            )

        if "BINANCE50_EXCHANGE" in os.environ:
            exc = os.environ["BINANCE50_EXCHANGE"].lower()
            if exc != "binance":
                raise ConfigError(f"Unsupported exchange: {exc}. Only binance is supported.")

        # Phase 4 new env overrides
        if "BINANCE_API_KEY" in os.environ:
            if "credentials" not in config_data:
                config_data["credentials"] = {}
            if "binance" not in config_data["credentials"]:
                config_data["credentials"]["binance"] = {}
            config_data["credentials"]["binance"]["api_key"] = os.environ["BINANCE_API_KEY"]

        if "BINANCE_API_SECRET" in os.environ:
            if "credentials" not in config_data:
                config_data["credentials"] = {}
            if "binance" not in config_data["credentials"]:
                config_data["credentials"]["binance"] = {}
            config_data["credentials"]["binance"]["api_secret"] = os.environ["BINANCE_API_SECRET"]

        if "BINANCE_API_KEY_LABEL" in os.environ:
            if "credentials" not in config_data:
                config_data["credentials"] = {}
            if "binance" not in config_data["credentials"]:
                config_data["credentials"]["binance"] = {}
            config_data["credentials"]["binance"]["api_key_label"] = os.environ[
                "BINANCE_API_KEY_LABEL"
            ]

        if "BINANCE_API_PERMISSION_READ" in os.environ:
            if "credentials" not in config_data:
                config_data["credentials"] = {}
            if "binance" not in config_data["credentials"]:
                config_data["credentials"]["binance"] = {}
            config_data["credentials"]["binance"]["permission_read"] = _parse_bool(
                os.environ["BINANCE_API_PERMISSION_READ"]
            )

        if "BINANCE_API_PERMISSION_SPOT_TRADE" in os.environ:
            if "credentials" not in config_data:
                config_data["credentials"] = {}
            if "binance" not in config_data["credentials"]:
                config_data["credentials"]["binance"] = {}
            config_data["credentials"]["binance"]["permission_spot_trade"] = _parse_bool(
                os.environ["BINANCE_API_PERMISSION_SPOT_TRADE"]
            )

        if "BINANCE_API_PERMISSION_FUTURES_TRADE" in os.environ:
            if "credentials" not in config_data:
                config_data["credentials"] = {}
            if "binance" not in config_data["credentials"]:
                config_data["credentials"]["binance"] = {}
            config_data["credentials"]["binance"]["permission_futures_trade"] = _parse_bool(
                os.environ["BINANCE_API_PERMISSION_FUTURES_TRADE"]
            )

        if "BINANCE_API_PERMISSION_MARGIN_TRADE" in os.environ:
            if "credentials" not in config_data:
                config_data["credentials"] = {}
            if "binance" not in config_data["credentials"]:
                config_data["credentials"]["binance"] = {}
            config_data["credentials"]["binance"]["permission_margin_trade"] = _parse_bool(
                os.environ["BINANCE_API_PERMISSION_MARGIN_TRADE"]
            )

        if "BINANCE_API_IP_RESTRICTED" in os.environ:
            if "credentials" not in config_data:
                config_data["credentials"] = {}
            if "binance" not in config_data["credentials"]:
                config_data["credentials"]["binance"] = {}
            config_data["credentials"]["binance"]["ip_restricted"] = _parse_bool(
                os.environ["BINANCE_API_IP_RESTRICTED"]
            )

        if "BINANCE_API_ALLOWED_IPS" in os.environ:
            if "credentials" not in config_data:
                config_data["credentials"] = {}
            if "binance" not in config_data["credentials"]:
                config_data["credentials"]["binance"] = {}
            config_data["credentials"]["binance"]["allowed_ips"] = _parse_ip_list(
                os.environ["BINANCE_API_ALLOWED_IPS"]
            )

        if "TELEGRAM_BOT_TOKEN" in os.environ:
            if "credentials" not in config_data:
                config_data["credentials"] = {}
            if "telegram" not in config_data["credentials"]:
                config_data["credentials"]["telegram"] = {}
            config_data["credentials"]["telegram"]["bot_token"] = os.environ["TELEGRAM_BOT_TOKEN"]

        if "TELEGRAM_CHAT_ID" in os.environ:
            if "credentials" not in config_data:
                config_data["credentials"] = {}
            if "telegram" not in config_data["credentials"]:
                config_data["credentials"]["telegram"] = {}
            config_data["credentials"]["telegram"]["chat_id"] = os.environ["TELEGRAM_CHAT_ID"]

        # Phase 4 Safety Env Vars
        safety_flags = {
            "BINANCE50_DRY_RUN": "dry_run",
            "BINANCE50_FORCE_PAPER_MODE": "force_paper_mode",
            "BINANCE50_DISABLE_ALL_ORDERS": "disable_all_orders",
            "BINANCE50_ALLOW_TESTNET_ORDERS": "allow_testnet_orders",
            "BINANCE50_ALLOW_DEMO_ORDERS": "allow_demo_orders",
            "BINANCE50_ALLOW_LIVE_ORDERS": "allow_live_orders",
        }
        for env_key, conf_key in safety_flags.items():
            if env_key in os.environ:
                if "safety" not in config_data:
                    config_data["safety"] = {}
                config_data["safety"][conf_key] = _parse_bool(os.environ[env_key])

        if "BINANCE50_LIVE_UNLOCK" in os.environ:
            # We don't map it directly into the config model itself if it's not a field,
            # but wait, it is NOT in the model according to the specs... wait,
            # we only check OS env in live_guard!
            # Or we can put it in config... Wait, spec says:
            # safety.require_manual_live_unlock: true ise env BINANCE50_LIVE_UNLOCK \
            # tam olarak required phrase olmalı.
            pass  # Checked in live_guard.py from os.environ

        if "BINANCE50_LIVE_RISK_ACK" in os.environ:
            pass  # Checked in live_guard.py from os.environ

        safety_floats = {
            "BINANCE50_MAX_DAILY_LOSS_PCT": "max_daily_loss_pct",
            "BINANCE50_MAX_POSITION_RISK_PCT": "max_position_risk_pct",
        }
        for env_key, conf_key in safety_floats.items():
            if env_key in os.environ:
                if "safety" not in config_data:
                    config_data["safety"] = {}
                config_data["safety"][conf_key] = float(os.environ[env_key])

        safety_ints = {
            "BINANCE50_MAX_OPEN_POSITIONS": "max_open_positions",
            "BINANCE50_MAX_ORDERS_PER_HOUR": "max_orders_per_hour",
        }
        for env_key, conf_key in safety_ints.items():
            if env_key in os.environ:
                if "safety" not in config_data:
                    config_data["safety"] = {}
                config_data["safety"][conf_key] = int(os.environ[env_key])

        app_config = AppConfig(**config_data)

        # Check if the profile resolves correctly to trigger validation errors
        _ = app_config.selected_environment_profile

        return app_config

    except Exception as e:
        raise ConfigError(f"Failed to load config: {str(e)}") from e
