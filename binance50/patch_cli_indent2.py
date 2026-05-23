with open("src/binance50/cli.py") as f:
    content = f.read()

import re

# find the offending def universe_explain
match = re.search(r"(def universe_explain[\s\S]*?)(@app\.command\(\))", content)
if match:
    block = match.group(1)
    new_block = []
    for line in block.split("\n"):
        if line.startswith("    from binance50.universe.blacklist"):
            pass  # let's just use regex to fix the indents in the whole file
