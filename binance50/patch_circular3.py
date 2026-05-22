with open("src/binance50/safety/stream_guard.py") as f:
    content = f.read()

content = content.replace("def build_stream_safety_report(config: AppConfig, plan: 'StreamSubscriptionPlan' | None = None) -> dict:", "from typing import Optional\n\ndef build_stream_safety_report(config: AppConfig, plan: Optional['StreamSubscriptionPlan'] = None) -> dict:")

with open("src/binance50/safety/stream_guard.py", "w") as f:
    f.write(content)
