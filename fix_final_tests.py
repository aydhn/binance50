with open("binance50/src/binance50/safety/api_key_guard.py", "r") as f:
    ak = f.read()

ak = ak.replace(
    'if profile.profile_name.value.endswith("_readonly") and (creds.permission_spot_trade or creds.permission_futures_trade):',
    'if profile.profile_name.value.endswith("_readonly") and \\\n       (creds.permission_spot_trade or creds.permission_futures_trade):'
)

with open("binance50/src/binance50/safety/api_key_guard.py", "w") as f:
    f.write(ak)

with open("binance50/src/binance50/safety/mode_guard.py", "r") as f:
    mg = f.read()

mg = mg.replace(
    'if mode == TradingMode.PAPER and not profile.is_paper and config.connector.order_gateway_enabled:',
    'if mode == TradingMode.PAPER and not profile.is_paper and \\\n       config.connector.order_gateway_enabled:'
)

mg = mg.replace(
    'if mode == TradingMode.TESTNET and not config.safety.allow_testnet_orders and config.connector.order_gateway_enabled:',
    'if mode == TradingMode.TESTNET and not config.safety.allow_testnet_orders and \\\n       config.connector.order_gateway_enabled:'
)

with open("binance50/src/binance50/safety/mode_guard.py", "w") as f:
    f.write(mg)


with open("binance50/src/binance50/safety/secrets_guard.py", "r") as f:
    sg = f.read()

sg = sg.replace(
    'if any(p in k_lower for p in secret_patterns) and isinstance(v, str) and not v.startswith("***") and v and len(v) > 0:',
    'if any(p in k_lower for p in secret_patterns) and \\\n           isinstance(v, str) and not v.startswith("***") and v and len(v) > 0:'
)

with open("binance50/src/binance50/safety/secrets_guard.py", "w") as f:
    f.write(sg)
