import sys
sys.path.insert(0, "binance50/src")
from binance50.config.models import AppConfig
c = AppConfig()
print(hasattr(c, "signals"))
