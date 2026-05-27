with open("binance50/src/binance50/ml/inference/reliability.py", "r") as f:
    content = f.read()

content = content.replace(
    "if start <= prob <= end (if i == bins - 1 else start <= prob < end):",
    "if (start <= prob <= end) if i == bins - 1 else (start <= prob < end):"
)

with open("binance50/src/binance50/ml/inference/reliability.py", "w") as f:
    f.write(content)
