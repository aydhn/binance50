from pathlib import Path

content = Path("binance50/src/binance50/cli.py").read_text()
# _get_repo_root is returning the wrong path because of src layout.
# __file__ is binance50/src/binance50/cli.py
# .parent -> binance50/src/binance50
# .parent -> binance50/src
# .parent -> binance50
# So .parent.parent.parent is the repo root.
content = content.replace(
    'return Path(__file__).resolve().parent.parent.parent.parent',
    'return Path(__file__).resolve().parent.parent.parent'
)
Path("binance50/src/binance50/cli.py").write_text(content)
