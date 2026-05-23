with open("src/binance50/cli.py") as f:
    content = f.read()

content = content.replace(
    "                from binance50.universe.blacklist import load_blacklist",
    "        from binance50.universe.blacklist import load_blacklist",
)

with open("src/binance50/cli.py", "w") as f:
    f.write(content)
