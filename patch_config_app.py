with open("binance50/src/binance50/config/models.py", "r") as f:
    content = f.read()

content = content.replace("class AppConfig(BaseModel):", "class AppConfig(BaseModel):\n    portfolio_sandbox: PortfolioSandboxConfig = Field(default_factory=PortfolioSandboxConfig)")

with open("binance50/src/binance50/config/models.py", "w") as f:
    f.write(content)
