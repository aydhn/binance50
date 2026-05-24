import re

with open("src/binance50/core/exceptions.py", "r") as f:
    content = f.read()

content = re.sub(
    r'def __init__\(self, message: str, details: dict \| None = None\) -> None:\n        super\(\)\.__init__\(message, "([A-Z_]+)", details\)',
    r'def __init__(self, message: str, details: dict | None = None) -> None:\n        super().__init__(message, details=details) # \1',
    content
)

with open("src/binance50/core/exceptions.py", "w") as f:
    f.write(content)
