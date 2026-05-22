from pathlib import Path

file_path = Path("src/binance50/cli.py")
content = file_path.read_text()

content = content.replace("print_json(data", "console.print_json(data")
file_path.write_text(content)
print("Patched CLI print_json")
