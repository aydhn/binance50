with open("src/binance50/cli.py") as f:
    content = f.read()

content = content.replace(
    "config = get_config()",
    "from binance50.config.loader import load_config\n    config = load_config()",
)

with open("src/binance50/cli.py", "w") as f:
    f.write(content)
