import re
with open("binance50/scripts/check_project.py", "r") as f:
    content = f.read()

# check for paper package
if "assert (SRC_DIR / \"safety\").exists()" in content and "assert (SRC_DIR / \"paper\").exists()" not in content:
    content = content.replace(
        "    assert (SRC_DIR / \"safety\").exists(), \"src/binance50/safety/ doesn't exist\"",
        "    assert (SRC_DIR / \"safety\").exists(), \"src/binance50/safety/ doesn't exist\"\n    assert (SRC_DIR / \"paper\").exists(), \"src/binance50/paper/ doesn't exist\""
    )

paper_commands = [
    "paper-config",
    "paper-intent-bridge-report",
    "paper-orders",
    "paper-fills",
    "paper-ledger",
    "paper-pnl-report",
    "paper-events",
    "paper-replay-report",
    "paper-quality-check",
    "paper-safety-check",
    "paper-gateway-safety-check",
]

for cmd in paper_commands:
    if f"'{cmd}'" not in content:
        # Find the execution_health check and insert paper checks after it
        if "['python', '-m', 'binance50.cli', 'execution-health']" in content:
             content = content.replace(
                "    run_command(['python', '-m', 'binance50.cli', 'execution-health'])",
                f"    run_command(['python', '-m', 'binance50.cli', 'execution-health'])\n    run_command(['python', '-m', 'binance50.cli', '{cmd}'])"
             )

with open("binance50/scripts/check_project.py", "w") as f:
    f.write(content)
