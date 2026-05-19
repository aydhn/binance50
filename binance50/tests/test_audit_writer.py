import json
import logging

from binance50.audit.events import AuditEvent, AuditEventType
from binance50.audit.writer import AuditWriter, audit_error, audit_event


def test_audit_event_to_dict():
    event = AuditEvent(
        event_type=AuditEventType.app_start,
        component="test",
        action="start",
        metadata={"secret": "should_be_redacted", "safe": "value"},
    )
    d = event.to_dict()
    assert d["event_type"] == "app_start"
    assert d["component"] == "test"
    assert d["action"] == "start"
    assert "event_id" in d
    assert "timestamp_utc" in d
    assert d["metadata"]["secret"] == "sh***REDACTED***ed"
    assert d["metadata"]["safe"] == "value"


def test_audit_writer_flush(tmp_path):
    log_file = tmp_path / "audit.jsonl"
    logger = logging.getLogger("test.audit")
    handler = logging.FileHandler(log_file)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    class JSONHandler(logging.FileHandler):
        def emit(self, record):
            self.stream.write(json.dumps(record.__dict__) + "\n")
            self.flush()

    json_handler = JSONHandler(log_file)
    logger.handlers = [json_handler]

    writer = AuditWriter(logger=logger)

    event = AuditEvent("test_event", "test_comp", "test_action")
    writer.write_event(event)

    content = log_file.read_text()
    assert "test_event" in content
    assert "test_comp" in content


def test_audit_event_helper(monkeypatch):
    events_written = []

    def mock_write(self, event):
        events_written.append(event)

    monkeypatch.setattr("binance50.audit.writer.AuditWriter.write_event", mock_write)

    audit_event("app_start", "core", "init", metadata={"token": "12345"})

    assert len(events_written) == 1
    event = events_written[0]
    assert event.event_type == "app_start"
    assert event.component == "core"
    assert "token" in event.metadata
    assert "***REDACTED***" in event.metadata["token"]


def test_audit_error_helper(monkeypatch):
    events_written = []

    def mock_write(self, event):
        events_written.append(event)

    monkeypatch.setattr("binance50.audit.writer.AuditWriter.write_event", mock_write)

    from binance50.core.exceptions import BinanceRateLimitError

    err = BinanceRateLimitError("Rate limited!")

    audit_error("error_captured", "api", "request", error=err, metadata={"api_key": "1234567890"})

    assert len(events_written) == 1
    event = events_written[0]
    assert event.event_type == "error_captured"
    assert event.component == "api"
    assert event.status == "failed"
    assert event.severity == "error"
    assert event.error_code == "BINANCE_RATE_LIMIT"
    assert event.exception_class == "BinanceRateLimitError"
    assert "api_key" in event.metadata
    assert "***REDACTED***" in event.metadata["api_key"]
