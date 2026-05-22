with open("src/binance50/cli.py") as f:
    content = f.read()

content = content.replace("    config = load_config()\n        config.runtime.market_scope = MarketScope(scope)", "    config = load_config()\n    config.runtime.market_scope = MarketScope(scope)")

with open("src/binance50/cli.py", "w") as f:
    f.write(content)
