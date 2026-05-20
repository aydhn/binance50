from binance50.config.loader import load_config
from binance50.network.clock import ClockSyncService

print("Loading config...")
config = load_config()
print("Creating ClockSyncService...")
service = ClockSyncService(config)
print("Getting report...")
print(service.to_report())
print("Done!")
