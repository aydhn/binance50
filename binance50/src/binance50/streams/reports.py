from binance50.config.models import AppConfig
from binance50.streams.buffer import StreamBuffer
from binance50.streams.metrics import StreamMetricsCollector
from binance50.streams.simulator import StreamSimulationResult
from binance50.streams.state import StreamStateStore
from binance50.streams.subscription import StreamSubscriptionPlan


def build_subscription_plan_report(plan: StreamSubscriptionPlan) -> dict:
    return {
        "plan_id": plan.plan_id,
        "market_scope": plan.market_scope.value,
        "use_combined": plan.use_combined,
        "total_subscriptions": len(plan.subscriptions),
        "combined_path": plan.combined_path,
        "created_at": plan.created_at_utc.isoformat(),
    }


def build_stream_buffer_report(buffer: StreamBuffer) -> dict:
    return buffer.to_report()


def build_stream_metrics_report(metrics: StreamMetricsCollector) -> dict:
    return metrics.snapshot().model_dump()


def build_stream_state_report(state_store: StreamStateStore) -> dict:
    return state_store.to_report()


def build_stream_simulation_report(result: StreamSimulationResult) -> dict:
    return result.model_dump()


def build_stream_health_report(
    config: AppConfig,
    metrics: StreamMetricsCollector | None = None,
    buffer: StreamBuffer | None = None,
) -> dict:
    return {
        "config": {
            "enabled": config.streams.enabled,
            "real_connect_enabled": config.streams.market_stream_real_connect_enabled,
            "use_combined": config.streams.use_combined_streams,
            "max_streams_spot": config.streams.max_streams_per_connection_spot,
            "max_streams_usdm": config.streams.max_streams_per_connection_usdm,
        },
        "buffer": buffer.to_report() if buffer else None,
        "metrics": metrics.snapshot().model_dump() if metrics else None,
    }
