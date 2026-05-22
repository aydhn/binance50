import re

with open('binance50/src/binance50/cli.py', 'r') as f:
    content = f.read()

content = content.replace("config = get_config()", "from binance50.cli import load_config\n    config = load_config()")

with open('binance50/src/binance50/cli.py', 'w') as f:
    f.write(content)
