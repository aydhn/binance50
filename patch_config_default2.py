with open("binance50/config/default.yaml", "r") as f:
    content = f.read()

# Wait, why was it failing? It looked for config/default.yaml but the script runs from binance50.
# The tests probably run from binance50 as well.
