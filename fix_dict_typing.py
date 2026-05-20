from pathlib import Path
import re

files = [
    "binance50/src/binance50/security/env_file.py",
    "binance50/src/binance50/security/live_unlock.py",
    "binance50/src/binance50/safety/mode_guard.py",
    "binance50/src/binance50/safety/dry_run_guard.py",
    "binance50/src/binance50/safety/api_key_guard.py",
    "binance50/src/binance50/safety/secrets_guard.py",
    "binance50/src/binance50/safety/live_guard.py",
    "binance50/src/binance50/safety/environment_guard.py",
]

for f in files:
    content = Path(f).read_text()
    if "from typing import Any" not in content:
        content = "from typing import Any\n" + content

    # Fix the sequence append error in secrets_guard
    if "secrets_guard" in f:
        content = re.sub(r'report = \{"status": "safe", "issues": \[\]\}', 'report: dict[str, Any] = {"status": "safe", "issues": []}', content)

    Path(f).write_text(content)
