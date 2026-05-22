import re

with open('binance50/src/binance50/cli.py', 'r') as f:
    content = f.read()

doctor_storage = """
    # Phase 10 Storage Check
    if config.storage.enabled:
         try:
             from binance50.safety.storage_guard import assert_storage_config_safe
             from binance50.storage.health import StorageHealthService
             assert_storage_config_safe(config)
             health = StorageHealthService(config).check()
             if health["status"] == "healthy":
                  console.print("[green]OK[/green] Storage check passed")
             else:
                  console.print("[yellow]WARN[/yellow] Storage check issues detected")
         except Exception as e:
             console.print(f"[red]FAIL[/red] Storage check failed: {e}")
             all_passed = False

"""

content = content.replace(
    "    if all_passed:",
    doctor_storage + "\n    if all_passed:"
)

with open('binance50/src/binance50/cli.py', 'w') as f:
    f.write(content)
