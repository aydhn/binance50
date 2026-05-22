with open("src/binance50/connectors/websocket_client.py") as f:
    content = f.read()


# Remove the import from top level, move it inside the methods where it is used
content = content.replace("from binance50.streams.subscription import StreamSubscriptionPlan\n", "")

# Change signature from typing to string or move import inside
content = content.replace("def build_stream_url_from_plan(self, plan: StreamSubscriptionPlan)", "def build_stream_url_from_plan(self, plan: 'StreamSubscriptionPlan')")
content = content.replace("def subscribe(self, plan: StreamSubscriptionPlan)", "def subscribe(self, plan: 'StreamSubscriptionPlan')")
content = content.replace("def unsubscribe(self, plan: StreamSubscriptionPlan)", "def unsubscribe(self, plan: 'StreamSubscriptionPlan')")
content = content.replace("def build_subscription_plan(self, symbols: list[str], stream_types: list, market_scope, interval=None) -> StreamSubscriptionPlan:", "def build_subscription_plan(self, symbols: list[str], stream_types: list, market_scope, interval=None) -> 'StreamSubscriptionPlan':")

with open("src/binance50/connectors/websocket_client.py", "w") as f:
    f.write("from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    from binance50.streams.subscription import StreamSubscriptionPlan\n\n" + content)
