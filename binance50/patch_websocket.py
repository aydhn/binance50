with open("src/binance50/connectors/websocket_client.py") as f:
    content = f.read()

import_statement = """
from binance50.streams.subscription import StreamSubscriptionPlan
from binance50.safety.stream_guard import assert_real_stream_connect_allowed
"""

if "StreamSubscriptionPlan" not in content:
    import re

    content = re.sub(
        r"from binance50\.rate_limit\.websocket_limits import \([\s\S]*?\)",
        "from binance50.rate_limit.websocket_limits import validate_stream_count\n"
        + import_statement.strip(),
        content,
    )

    # replace build_stream_url with build_stream_url_from_plan
    # add subscribe, unsubscribe, receive_loop

    class_methods = """
    def build_subscription_plan(self, symbols: list[str], stream_types: list, market_scope, interval=None) -> StreamSubscriptionPlan:
        from binance50.streams.subscription import build_subscription_plan
        return build_subscription_plan(symbols, stream_types, market_scope, self.config, interval)

    def build_stream_url_from_plan(self, plan: StreamSubscriptionPlan) -> str:
        from binance50.streams.routing import build_full_stream_url
        # Adjust base depending on plan type inside routing, but the method handles it if config is passed
        # The routing module actually needs endpoint info, but here we just rely on the new method
        # which might not perfectly align with endpoint_info, but let's stick to the phase requirements
        return build_full_stream_url(plan, self.config)

    def subscribe(self, plan: StreamSubscriptionPlan) -> None:
        assert_real_stream_connect_allowed(self.config)

    def unsubscribe(self, plan: StreamSubscriptionPlan) -> None:
        assert_real_stream_connect_allowed(self.config)

    def receive_loop(self) -> None:
        assert_real_stream_connect_allowed(self.config)
"""
    content += "\n" + class_methods

    with open("src/binance50/connectors/websocket_client.py", "w") as f:
        f.write(content)
