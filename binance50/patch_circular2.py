with open("src/binance50/safety/stream_guard.py") as f:
    content = f.read()

content = content.replace(
    "from binance50.streams.subscription import StreamSubscriptionPlan",
    "from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    from binance50.streams.subscription import StreamSubscriptionPlan",
)
content = content.replace(
    "def assert_subscription_plan_safe(plan: StreamSubscriptionPlan, config: AppConfig) -> None:",
    "def assert_subscription_plan_safe(plan: 'StreamSubscriptionPlan', config: AppConfig) -> None:",
)
content = content.replace(
    "def build_stream_safety_report(config: AppConfig, plan: StreamSubscriptionPlan | None = None) -> dict:",
    "def build_stream_safety_report(config: AppConfig, plan: 'StreamSubscriptionPlan' | None = None) -> dict:",
)

with open("src/binance50/safety/stream_guard.py", "w") as f:
    f.write(content)
