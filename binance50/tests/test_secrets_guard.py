from pathlib import Path

import pytest

from binance50.core.exceptions import GitIgnorePolicyError, SecretLeakError
from binance50.safety.secrets_guard import (
    build_secret_safety_report,
    detect_secret_like_values_in_file,
    validate_env_example_has_no_real_secrets,
    validate_no_secret_in_mapping,
)
from binance50.security.gitignore import assert_env_ignored


def test_validate_env_example_has_no_real_secrets(tmp_path: Path):
    env_file = tmp_path / ".env.example"
    env_file.write_text("BINANCE_API_KEY=your_api_key_here\n")
    validate_env_example_has_no_real_secrets(env_file)

    env_file.write_text("BINANCE_API_KEY=" + "A" * 65 + "\n")
    with pytest.raises(SecretLeakError):
        validate_env_example_has_no_real_secrets(env_file)


def test_assert_env_ignored(tmp_path: Path):
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("node_modules\n")
    with pytest.raises(GitIgnorePolicyError):
        assert_env_ignored(tmp_path)

    gitignore.write_text(".env\n.env.*\n")
    assert_env_ignored(tmp_path)


def test_validate_no_secret_in_mapping():
    safe_mapping = {"api_key": "***redacted***"}
    validate_no_secret_in_mapping(safe_mapping)

    unsafe_mapping = {"api_key": "mysecretkey"}
    with pytest.raises(SecretLeakError):
        validate_no_secret_in_mapping(unsafe_mapping)

    nested_unsafe_mapping = {"config": {"secret": "mysecretkey"}}
    with pytest.raises(SecretLeakError):
        validate_no_secret_in_mapping(nested_unsafe_mapping)


def test_detect_secret_like_values(tmp_path: Path):
    file = tmp_path / "test.txt"
    file.write_text("some random text\n")
    assert not detect_secret_like_values_in_file(file)

    file.write_text("secret: " + "a" * 64 + "\n")
    assert detect_secret_like_values_in_file(file)


def test_build_secret_safety_report(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("BINANCE50_ENV", "local")

    (tmp_path / ".env.example").write_text("KEY=your_key")
    (tmp_path / ".gitignore").write_text(".env\n.env.*")
    (tmp_path / "config").mkdir()

    # We must mock the environments.yaml so profile is found
    (tmp_path / "config" / "environments.yaml").write_text("""
default_profile: local_paper_spot
profiles:
  local_paper_spot:
    profile_name: local_paper_spot
    exchange: binance
    runtime_environment: local
    trading_mode: paper
    market_scope: spot
    account_domain: spot
    endpoints:
      rest_base_url: null
      rest_fallback_urls: []
      websocket_market_base_url: null
      websocket_user_base_url: null
    is_testnet: false
    is_mainnet: false
    is_paper: true
    is_live: false
    allows_real_orders: false
    requires_api_key: false
    requires_api_secret: false
    requires_live_guard: false
    supports_user_data_stream: false
    supports_market_stream: false
    supports_order_placement: false
    permission_level: no_credentials
""")
    (tmp_path / "config" / "default.yaml").write_text("project:\n  name: test")

    from binance50.config.loader import load_config

    config = load_config(str(tmp_path / "config"))

    report = build_secret_safety_report(config, tmp_path)
    assert report["status"] == "safe"
