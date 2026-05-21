import os
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import SecretLeakError
from binance50.security.gitignore import assert_env_ignored


def check_for_leaked_secrets() -> list[str]:
    """Check if real secrets are present in environment variables."""
    warnings = []

    sensitive_keys = ["BINANCE_API_KEY", "BINANCE_API_SECRET", "TELEGRAM_BOT_TOKEN"]
    placeholders = ["your_api_key_here", "your_api_secret_here", "changeme", ""]

    for key in sensitive_keys:
        val = os.environ.get(key, "")
        if val and val not in placeholders and len(val) > 20 and not bool(re.search(r"\s", val)):
            warnings.append(
                f"Warning: Suspiciously long value found for {key}. Ensure this is not logged."
            )

    return warnings


def validate_env_example_has_no_real_secrets(path: Path) -> None:
    if not path.exists():
        return

    with open(path, encoding="utf-8") as f:
        content = f.read()

    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        parts = line.split("=", 1)
        if len(parts) == 2:
            key, val = parts
            val = val.strip()
            if len(val) > 40 and "your" not in val.lower():
                raise SecretLeakError(f"Potential secret leak in {path} for key {key}")


def verify_no_secrets_in_example_env(filepath: str = ".env.example") -> bool:
    validate_env_example_has_no_real_secrets(Path(filepath))
    return True


def validate_gitignore_protects_env(repo_root: Path) -> None:
    assert_env_ignored(repo_root)


def validate_no_secret_in_mapping(mapping: Mapping[str, Any]) -> None:
    secret_patterns = ["secret", "api_key", "token", "password", "signature", "x-mbx-apikey"]

    for k, v in mapping.items():
        k_lower = str(k).lower()
        if (
            any(p in k_lower for p in secret_patterns)
            and isinstance(v, str)
            and not v.startswith("***")
            and v
            and len(v) > 0
        ):
            # Make sure it's not actually an empty string
            raise SecretLeakError(f"Unredacted secret found in mapping for key: {k}")
        if isinstance(v, dict):
            validate_no_secret_in_mapping(v)
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    validate_no_secret_in_mapping(item)


def validate_loaded_secrets_are_redacted(config: AppConfig) -> None:
    # AppConfig model_dump should not expose secrets as plain string if using SecretStr.
    # We serialize the config using model_dump(mode="json") and verify.
    dumped = config.model_dump(mode="json")
    validate_no_secret_in_mapping(dumped)


def detect_secret_like_values_in_file(path: Path) -> list[str]:
    """Scan a file for typical secret patterns (e.g. 64 char hex)."""
    if not path.exists():
        return []

    found = []
    content = path.read_text(encoding="utf-8", errors="replace")

    # 64-char hex string often used for secrets
    hex_64 = re.compile(r"\b[a-fA-F0-9]{64}\b")
    for _match in hex_64.finditer(content):
        found.append(f"Suspicious 64-char hex in {path.name}")

    return found


def build_secret_safety_report(config: AppConfig, repo_root: Path) -> dict[str, Any]:
    report: dict[str, Any] = {"status": "safe", "issues": []}

    try:
        validate_env_example_has_no_real_secrets(repo_root / ".env.example")
    except Exception as e:
        report["issues"].append(str(e))

    try:
        validate_gitignore_protects_env(repo_root)
    except Exception as e:
        report["issues"].append(str(e))

    try:
        validate_loaded_secrets_are_redacted(config)
    except Exception as e:
        report["issues"].append(str(e))

    if report["issues"]:
        report["status"] = "unsafe"

    return report


def assert_secret_policy(config: AppConfig, repo_root: Path) -> None:
    validate_env_example_has_no_real_secrets(repo_root / ".env.example")
    validate_gitignore_protects_env(repo_root)
    validate_loaded_secrets_are_redacted(config)
