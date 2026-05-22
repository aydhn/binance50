from pathlib import Path

file_path = Path("src/binance50/universe/cache.py")
content = file_path.read_text()

if "from binance50.config.models import UniverseConfig" in content:
    content = content.replace("from binance50.config.models import UniverseConfig", "from binance50.config.models import AppConfig, UniverseConfig")

file_path.write_text(content)
print("Patched universe cache")
