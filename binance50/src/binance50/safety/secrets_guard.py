import os
import re

from binance50.core.exceptions import SecretLeakError


def check_for_leaked_secrets() -> list[str]:
    """Check if real secrets are present in environment variables."""
    warnings = []

    # Check for suspiciously long values in sensitive env vars
    sensitive_keys = ["BINANCE_API_KEY", "BINANCE_API_SECRET", "TELEGRAM_BOT_TOKEN"]

    placeholders = ["your_api_key_here", "your_api_secret_here", "changeme", ""]

    for key in sensitive_keys:
        val = os.environ.get(key, "")
        if val and val not in placeholders and len(val) > 20 and not bool(re.search(r"\s", val)):
            warnings.append(
                f"Warning: Suspiciously long value found for {key}. Ensure this is not logged."
            )

    return warnings


def verify_no_secrets_in_example_env(filepath: str = ".env.example") -> bool:
    """Verify that .env.example contains no real secrets."""
    if not os.path.exists(filepath):
        return True

    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # Check if there are values longer than 40 chars which might be real keys
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        parts = line.split("=", 1)
        if len(parts) == 2:
            key, val = parts
            if len(val) > 40 and "your" not in val.lower():
                raise SecretLeakError(f"Potential secret leak in {filepath} for key {key}")

    return True
