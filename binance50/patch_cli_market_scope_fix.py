with open("src/binance50/cli.py") as f:
    content = f.read()

import_statement = """
from binance50.core.enums import MarketScope
"""

if "from binance50.core.enums import MarketScope" not in content:
    lines = content.split("\n")
    import_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("import") or line.startswith("from"):
            import_idx = i
    lines.insert(import_idx + 1, import_statement)
    content = "\n".join(lines)
    with open("src/binance50/cli.py", "w") as f:
        f.write(content)
