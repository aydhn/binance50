with open("binance50/src/binance50/cli.py", "r") as f:
    cli = f.read()

cli = cli.replace(
    '"\\n[bold red]HIGH RISK: Live unlock guard is OPEN. Live trading is structurally allowed by unlock locks![/bold red]"',
    '"\\n[bold red]HIGH RISK: Live unlock guard is OPEN. " \\\n                "Live trading is structurally allowed by unlock locks![/bold red]"'
)

with open("binance50/src/binance50/cli.py", "w") as f:
    f.write(cli)


with open("binance50/src/binance50/safety/mode_guard.py", "r") as f:
    mg = f.read()

mg = mg.replace(
    '"Testnet trading is active, but allow_testnet_orders is false while order_gateway is enabled."',
    '"Testnet trading is active, but allow_testnet_orders is false " \\\n                "while order_gateway is enabled."'
)

with open("binance50/src/binance50/safety/mode_guard.py", "w") as f:
    f.write(mg)
