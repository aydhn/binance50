with open("binance50/src/binance50/config/models.py", "r") as f:
    content = f.read()

# Make sure AppConfig actually includes the new SignalsConfig
if "signals: SignalsConfig" not in content:
    content = content.replace("strategies: StrategiesConfig = Field(default_factory=StrategiesConfig)", "strategies: StrategiesConfig = Field(default_factory=StrategiesConfig)\n    signals: SignalsConfig = Field(default_factory=SignalsConfig)")
    with open("binance50/src/binance50/config/models.py", "w") as f:
        f.write(content)
