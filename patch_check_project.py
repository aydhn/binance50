import re

with open('binance50/scripts/check_project.py', 'r') as f:
    content = f.read()

storage_checks = """
    # Phase 10: Storage
    check_command(["python", "-m", "binance50.cli", "storage-config"], "Storage config")
    check_command(["python", "-m", "binance50.cli", "storage-init"], "Storage init")
    check_command(["python", "-m", "binance50.cli", "storage-health"], "Storage health")
    check_command(["python", "-m", "binance50.cli", "storage-import-ohlcv-fixture", "--symbol", "BTCUSDT", "--scope", "spot", "--interval", "1m", "--fixture", "ohlcv_spot_btcusdt_1m_sample.json"], "Storage import OHLCV")
    check_command(["python", "-m", "binance50.cli", "storage-list-datasets"], "Storage list datasets")
    check_command(["python", "-m", "binance50.cli", "storage-dataset-summary", "--dataset", "ohlcv"], "Storage dataset summary")
    check_command(["python", "-m", "binance50.cli", "storage-integrity-check"], "Storage integrity check")
    check_command(["python", "-m", "binance50.cli", "storage-safety-check"], "Storage safety check")
"""

content = content.replace(
    "    print(\"\\nAll checks passed successfully!\\n\")",
    storage_checks + "\n    print(\"\\nAll checks passed successfully!\\n\")"
)

with open('binance50/scripts/check_project.py', 'w') as f:
    f.write(content)
