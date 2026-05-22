from binance50.config.models import AppConfig
from binance50.safety.stream_guard import (
    assert_real_stream_connect_allowed,
    assert_subscription_plan_safe,
)
from binance50.streams.lifecycle import StreamConnectionLifecycle, build_stream_lifecycle
from binance50.streams.subscription import StreamSubscriptionPlan


class StreamConnectionManager:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._lifecycles: dict[str, StreamConnectionLifecycle] = {}
        self._active_plans: dict[str, StreamSubscriptionPlan] = {}

    def prepare_connection(self, plan: StreamSubscriptionPlan) -> StreamConnectionLifecycle:
        assert_subscription_plan_safe(plan, self.config)
        lifecycle = build_stream_lifecycle(self.config)
        self._lifecycles[lifecycle.connection_id] = lifecycle
        self._active_plans[lifecycle.connection_id] = plan
        return lifecycle

    def start(self, plan: StreamSubscriptionPlan) -> str:
        assert_real_stream_connect_allowed(self.config)
        # Should not reach here in Phase 9
        return "not_reached"

    def stop(self, connection_id: str) -> None:
        if connection_id in self._lifecycles:
            self._lifecycles[connection_id].status = "stopped"

    def status(self) -> dict:
        return {
            "active_connections": len([l for l in self._lifecycles.values() if l.status == "active"]),
            "total_connections_tracked": len(self._lifecycles)
        }

    def reconnect_if_needed(self) -> dict:
        return {"reconnected": 0}
