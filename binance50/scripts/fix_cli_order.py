import sys
from pathlib import Path

file_path = Path("src/binance50/cli.py")
content = file_path.read_text()

# Remove the if __name__ block
content = content.replace("if __name__ == \"__main__\":\n    app()\n\n", "")

# Add it back to the very end
content += "\nif __name__ == \"__main__\":\n    app()\n"

file_path.write_text(content)
print("Patched CLI order")
