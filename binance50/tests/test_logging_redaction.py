import pytest

from binance50.core.exceptions import SecretLeakError
from binance50.logging.redaction import (
    assert_no_secret_leak,
    contains_potential_secret,
    is_sensitive_key,
    normalize_sensitive_key,
    redact_mapping,
    redact_sequence,
    redact_text,
)


def test_normalize_sensitive_key():
    assert normalize_sensitive_key("API-Key") == "api_key"
    assert normalize_sensitive_key("api_secret") == "api_secret"
    assert normalize_sensitive_key("ListenKey") == "listenkey"


def test_is_sensitive_key():
    assert is_sensitive_key("API_KEY") is True
    assert is_sensitive_key("my_secret_token") is True
    assert is_sensitive_key("chat_id") is True
    assert is_sensitive_key("regular_field") is False


def test_redact_text_key_value():
    text = "Connecting with api_key=12345abcde&other=value"
    redacted = redact_text(text)
    assert "api_key=***REDACTED***" in redacted
    assert "other=value" in redacted

    text = "Header X-MBX-APIKEY: 12345abcde"
    redacted = redact_text(text)
    assert "X-MBX-APIKEY: ***REDACTED***" in redacted


def test_redact_text_json():
    text = '{"api_key": "12345abcde", "normal": "value"}'
    redacted = redact_text(text)
    assert '"api_key":"***REDACTED***"' in redacted.replace(" ", "")
    assert '"normal": "value"' in redacted

    text2 = "{'secret': 'my_super_secret'}"
    redacted2 = redact_text(text2)
    assert "'secret':'***REDACTED***'" in redacted2.replace(" ", "")


def test_redact_text_patterns():
    # Binance key pattern (64 chars)
    long_key = "A" * 64
    text = f"My key is {long_key}"
    redacted = redact_text(text)
    assert "***REDACTED***" in redacted
    assert long_key not in redacted

    # Telegram bot token pattern
    bot_token = "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"
    text = f"Bot token: {bot_token}"
    redacted = redact_text(text)
    assert "***REDACTED***" in redacted
    assert bot_token not in redacted


def test_redact_mapping():
    data = {
        "api_key": "my_secret_key",
        "nested": {"token": "my_secret_token", "safe": "value"},
        "safe_key": "safe_value",
    }
    redacted = redact_mapping(data)
    assert redacted["api_key"] == "my***REDACTED***ey"
    assert redacted["nested"]["token"] == "my***REDACTED***en"
    assert redacted["nested"]["safe"] == "value"
    assert redacted["safe_key"] == "safe_value"


def test_redact_sequence():
    data = ["api_key=12345", {"secret": "my_secret"}, ["nested", "token=12345"]]
    redacted = redact_sequence(data)
    assert "api_key=***REDACTED***" in redacted[0]
    assert redacted[1]["secret"] == "my***REDACTED***et"
    assert "token=***REDACTED***" in redacted[2][1]


def test_contains_potential_secret():
    assert contains_potential_secret("api_key=123") is True
    assert contains_potential_secret("API_SECRET: 123") is True
    assert contains_potential_secret('{"token": "abc"}') is True
    assert contains_potential_secret("normal text") is False
    assert contains_potential_secret("1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789") is True


def test_assert_no_secret_leak():
    with pytest.raises(SecretLeakError):
        assert_no_secret_leak("api_key=123")

    # Should not raise
    assert_no_secret_leak("normal text")
