from pathlib import Path

file_path = Path("src/binance50/config/models.py")
content = file_path.read_text()

content = content.replace("            indicators: IndicatorsConfig = Field(default_factory=IndicatorsConfig)\n    def validate_live_trading(self) -> \"AppConfig\":", "    def validate_live_trading(self) -> \"AppConfig\":")
content = content.replace("    storage: StorageConfig = StorageConfig()", "    storage: StorageConfig = StorageConfig()\n    indicators: IndicatorsConfig = Field(default_factory=IndicatorsConfig)")

file_path.write_text(content)
print("Fixed AppConfig indentation")
