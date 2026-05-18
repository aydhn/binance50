import logging
import logging.config
from pathlib import Path

import yaml

from binance50.logging.redaction import redact_text


class RedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact_text(str(record.msg))
        if isinstance(record.args, dict):
            # In phase 1 we just keep it simple
            pass
        return True


def setup_logging(config_path: str = "config/logging.yaml") -> None:
    path = Path(config_path)
    if path.exists():
        with open(path, encoding="utf-8") as f:
            config = yaml.safe_load(f)

        # Ensure log dir exists
        for handler in config.get("handlers", {}).values():
            if "filename" in handler:
                log_file = Path(handler["filename"])
                log_file.parent.mkdir(parents=True, exist_ok=True)

        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=logging.INFO)

    # Apply redacting filter to all handlers of binance50 logger
    logger = logging.getLogger("binance50")
    redacting_filter = RedactingFilter()
    for handler in logger.handlers:
        handler.addFilter(redacting_filter)

    # Also add to root just in case
    for handler in logging.getLogger().handlers:
        handler.addFilter(redacting_filter)
