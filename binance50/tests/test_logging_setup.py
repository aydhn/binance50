import json
import logging

from binance50.logging.context import set_correlation_id, set_runtime_context
from binance50.logging.setup import setup_logging, shutdown_logging


def test_logging_setup_files_created(tmp_path):
    # Create a test config
    config_yaml = f"""
version: 1
disable_existing_loggers: false
root_level: INFO
console:
  enabled: false
file:
  enabled: true
  level: DEBUG
  log_dir: {tmp_path}/logs
  app_log_file: binance50.log
  error_log_file: binance50_error.log
audit:
  enabled: true
  audit_dir: {tmp_path}/logs
  audit_file: binance50_audit.jsonl
format:
  json_enabled: true
"""
    config_file = tmp_path / "logging.yaml"
    config_file.write_text(config_yaml)

    # Ensure clean state
    shutdown_logging()

    # Setup
    setup_logging(str(config_file))

    # Check handlers don't duplicate on second call
    root_handlers_count = len(logging.getLogger().handlers)
    setup_logging(str(config_file))
    assert len(logging.getLogger().handlers) == root_handlers_count

    # Set context
    cid = set_correlation_id("test-corr-id")
    set_runtime_context("test_profile", "test_mode", "test_scope")

    # Log something
    logger = logging.getLogger("binance50.test")
    logger.info("Test info message")
    logger.error("Test error message")

    # Force flush
    for handler in logging.getLogger().handlers:
        handler.flush()

    # Check app log
    app_log = tmp_path / "logs" / "binance50.log"
    assert app_log.exists()
    content = app_log.read_text()
    assert "Test info message" in content
    assert "Test error message" in content

    # Check JSON format
    last_line = content.strip().split("\n")[-1]
    parsed = json.loads(last_line)
    assert parsed["message"] == "Test error message"
    assert parsed["correlation_id"] == "test-corr-id"
    assert parsed["environment_profile"] == "test_profile"
    assert parsed["trading_mode"] == "test_mode"

    # Check error log
    err_log = tmp_path / "logs" / "binance50_error.log"
    assert err_log.exists()
    err_content = err_log.read_text()
    assert "Test info message" not in err_content
    assert "Test error message" in err_content

    # Clean up
    shutdown_logging()
