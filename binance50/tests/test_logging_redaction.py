from binance50.logging.redaction import redact_mapping, redact_text, redact_value


def test_redact_value():
    assert redact_value("1234") == "***"
    assert redact_value("12345") == "12*45"
    assert redact_value("abcde12345") == "ab******45"


def test_redact_mapping():
    data = {
        "api_key": "mysecretkey",
        "normal_key": "normalvalue",
        "nested": {"token": "mysecrettoken"},
    }
    redacted = redact_mapping(data)
    assert redacted["api_key"] == "my*******ey"
    assert redacted["normal_key"] == "normalvalue"
    assert redacted["nested"]["token"] == "my*********en"


def test_redact_text():
    text = "Here is my api_key=supersecretvalue and chat_id=123456"
    redacted = redact_text(text)
    assert "supersecretvalue" not in redacted
    assert "api_key=***" in redacted
    assert "123456" not in redacted
    assert "chat_id=***" in redacted

    text_json = '{"API_SECRET": "mysecretpassword123"}'
    redacted_json = redact_text(text_json)
    assert "mysecretpassword123" not in redacted_json
    assert '"API_SECRET": "***"' in redacted_json
