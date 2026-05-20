with open("binance50/src/binance50/safety/api_key_guard.py", "r") as f:
    ak = f.read()

ak = ak.replace(
    'if profile.profile_name.value.endswith("_readonly"):\n        if creds.permission_spot_trade or creds.permission_futures_trade:',
    'if profile.profile_name.value.endswith("_readonly") and (creds.permission_spot_trade or creds.permission_futures_trade):'
)

with open("binance50/src/binance50/safety/api_key_guard.py", "w") as f:
    f.write(ak)

with open("binance50/src/binance50/safety/mode_guard.py", "r") as f:
    mg = f.read()

mg = mg.replace(
    'if mode == TradingMode.PAPER and not profile.is_paper:\n        # Paper mode can run against testnet/live profiles if we don\'t send orders\n        # But we must verify that order_gateway is completely disabled in this configuration\n        if config.connector.order_gateway_enabled:',
    'if mode == TradingMode.PAPER and not profile.is_paper and config.connector.order_gateway_enabled:\n        # Paper mode can run against testnet/live profiles if we don\'t send orders\n        # But we must verify that order_gateway is completely disabled in this configuration'
)

mg = mg.replace(
    'if mode == TradingMode.TESTNET and not config.safety.allow_testnet_orders:\n        if config.connector.order_gateway_enabled:',
    'if mode == TradingMode.TESTNET and not config.safety.allow_testnet_orders and config.connector.order_gateway_enabled:'
)

with open("binance50/src/binance50/safety/mode_guard.py", "w") as f:
    f.write(mg)


with open("binance50/src/binance50/safety/secrets_guard.py", "r") as f:
    sg = f.read()

sg = sg.replace(
    'if any(p in k_lower for p in secret_patterns):\n            if isinstance(v, str) and not v.startswith("***"):\n                # Make sure it\'s not actually an empty string\n                if v and len(v) > 0:',
    'if any(p in k_lower for p in secret_patterns) and isinstance(v, str) and not v.startswith("***") and v and len(v) > 0:'
)

with open("binance50/src/binance50/safety/secrets_guard.py", "w") as f:
    f.write(sg)
