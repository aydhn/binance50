cd binance50
pytest
mypy src
ruff check .
black --check .
