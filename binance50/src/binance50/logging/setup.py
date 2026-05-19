import logging
import logging.config
import logging.handlers
import sys
from pathlib import Path
from typing import Any

import yaml

from binance50.core.exceptions import LoggingSetupError
from binance50.logging.filters import CorrelationIdFilter, RedactionFilter, RuntimeContextFilter
from binance50.logging.formatters import SafeConsoleFormatter, SafeJsonFormatter


def _create_log_dirs(config: dict[str, Any]) -> None:
    try:
        if config.get("file", {}).get("enabled", False):
            log_dir = Path(config["file"].get("log_dir", "logs"))
            log_dir.mkdir(parents=True, exist_ok=True)

        if config.get("audit", {}).get("enabled", False):
            audit_dir = Path(config["audit"].get("audit_dir", "logs"))
            audit_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise LoggingSetupError(f"Failed to create log directories: {e}")


_logging_configured = False


def setup_logging(config_path: str = "config/logging.yaml", app_config: Any = None) -> None:
    from typing import cast
    global _logging_configured
    if _logging_configured:
        return

    path = Path(config_path)

    # Defaults
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "root_level": "INFO",
        "console": {"enabled": True, "level": "INFO"},
        "file": {"enabled": False},
        "audit": {"enabled": False},
    }

    if path.exists():
        with open(path, encoding="utf-8") as f:
            yaml_config = yaml.safe_load(f)
            if yaml_config:
                logging_config.update(yaml_config)

    try:
        _create_log_dirs(logging_config)
    except LoggingSetupError as e:
        print(f"CRITICAL: Logging setup failed: {e}", file=sys.stderr)
        raise

    root_logger = logging.getLogger()
    root_logger.setLevel(cast(str, logging_config.get("root_level", "INFO")))

    # Clear existing handlers
    root_logger.handlers.clear()

    filters = [RedactionFilter(), CorrelationIdFilter(), RuntimeContextFilter()]

    if cast(dict[str, Any], logging_config.get("console", {})).get("enabled", True):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(cast(dict[str, Any], logging_config.get("console", {})).get("level", "INFO"))
        fmt_str = cast(dict[str, Any], logging_config.get("format", {})).get(
            "console_format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(SafeConsoleFormatter(fmt=fmt_str))
        for filt in filters:
            console_handler.addFilter(filt)
        root_logger.addHandler(console_handler)

    if cast(dict[str, Any], logging_config.get("file", {})).get("enabled", True):
        file_cfg = cast(dict[str, Any], logging_config["file"])
        log_dir = Path(file_cfg.get("log_dir", "logs"))
        max_bytes = file_cfg.get("max_bytes", 10485760)
        backup_count = file_cfg.get("backup_count", 5)

        # App handler
        app_log_file = log_dir / file_cfg.get("app_log_file", "binance50.log")
        app_handler = logging.handlers.RotatingFileHandler(
            app_log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        app_handler.setLevel(file_cfg.get("level", "DEBUG"))

        # Error handler
        error_log_file = log_dir / file_cfg.get("error_log_file", "binance50_error.log")
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)

        if cast(dict[str, Any], logging_config.get("format", {})).get("json_enabled", True):
            formatter = SafeJsonFormatter()
        else:
            fmt_str = cast(dict[str, Any], logging_config.get("format", {})).get(
                "file_format",
                "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
            )
            formatter = SafeConsoleFormatter(fmt=fmt_str)  # type: ignore

        app_handler.setFormatter(formatter)
        error_handler.setFormatter(formatter)

        for filt in filters:
            app_handler.addFilter(filt)
            error_handler.addFilter(filt)

        root_logger.addHandler(app_handler)
        root_logger.addHandler(error_handler)

    # We will handle audit in a separate writer, but we can set up an audit logger
    if cast(dict[str, Any], logging_config.get("audit", {})).get("enabled", True):
        audit_cfg = cast(dict[str, Any], logging_config["audit"])
        audit_dir = Path(audit_cfg.get("audit_dir", "logs"))
        audit_file = audit_dir / audit_cfg.get("audit_file", "binance50_audit.jsonl")

        audit_handler = logging.handlers.RotatingFileHandler(
            audit_file,
            maxBytes=cast(dict[str, Any], logging_config.get("file", {})).get("max_bytes", 10485760),
            backupCount=cast(dict[str, Any], logging_config.get("file", {})).get("backup_count", 5),
            encoding="utf-8",
        )
        audit_handler.setLevel(logging.INFO)
        # Audit logs should strictly be JSON
        audit_handler.setFormatter(SafeJsonFormatter())
        # Apply filters just in case
        for filt in filters:
            audit_handler.addFilter(filt)

        audit_logger = logging.getLogger("binance50.audit")
        audit_logger.setLevel(logging.INFO)
        audit_logger.propagate = False  # Do not send to root logger
        audit_logger.handlers.clear()
        audit_logger.addHandler(audit_handler)

    _logging_configured = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def shutdown_logging() -> None:
    global _logging_configured
    logging.shutdown()
    _logging_configured = False
