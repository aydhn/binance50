from pathlib import Path

file_path = Path("src/binance50/indicators/adapters/native.py")
content = file_path.read_text()

content = content.replace(
    "res = res.to_frame(name=res.name)", "res = res.to_frame(name=spec.output_columns[0])"
)

file_path.write_text(content)
print("Patched native adapter")
