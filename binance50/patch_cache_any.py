from pathlib import Path

file_path = Path("src/binance50/universe/cache.py")
content = file_path.read_text()

if "import json" in content:
    content = content.replace("import json", "import json\nfrom typing import Any")
else:
    content = "from typing import Any\n" + content

file_path.write_text(content)
print("Patched universe cache Any")
