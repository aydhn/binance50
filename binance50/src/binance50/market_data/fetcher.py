import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from binance50.config.models import AppConfig
from binance50.connectors.request_models import ConnectorRequest
from binance50.connectors.rest_client import BinanceRestClient
from binance50.core.enums import MarketScope
from binance50.core.exceptions import MarketDataFetchDisabledError, OHLCVParseError
from binance50.market_data.fetch_plan import OHLCVFetchChunk, OHLCVFetchPlan
from binance50.market_data.kline_parser import parse_kline_payload
from binance50.market_data.ohlcv_models import (
    OHLCVFetchRequest,
    OHLCVFetchResult,
    OHLCVSource,
)


class OHLCVFetcher:
    def __init__(
        self,
        config: AppConfig,
        rest_client: BinanceRestClient,
        rate_limiter: Any = None,
        retry_controller: Any = None,
        request_budget_checker: Any = None,
    ) -> None:
        self.config = config
        self.rest_client = rest_client
        self.rate_limiter = rate_limiter
        self.retry_controller = retry_controller
        self.request_budget_checker = request_budget_checker

    def build_request(self, chunk: OHLCVFetchChunk) -> ConnectorRequest:
        from binance50.core.enums import MarketScope

        scope = MarketScope.SPOT if "api/v3" in chunk.endpoint_path else MarketScope.USDM_FUTURES
        return self.rest_client.build_public_kline_request(
            symbol=chunk.symbol,
            market_scope=scope,
            interval=chunk.interval,
            start_time_ms=chunk.start_time_ms,
            end_time_ms=chunk.end_time_ms,
            limit=chunk.limit,
        )

    def fetch_chunk(self, chunk: OHLCVFetchChunk) -> OHLCVFetchResult:
        if not self.config.market_data.real_fetch_enabled:
            raise MarketDataFetchDisabledError(
                "Real market data fetch is disabled. Use fixtures or enable real_fetch_enabled in config."
            )

        # Real fetch logic would go here. For now, it's blocked by the exception above.
        raise MarketDataFetchDisabledError(
            "Real fetch is not implemented in Phase 8 default safety."
        )

    def fetch_plan(self, plan: OHLCVFetchPlan) -> list[OHLCVFetchResult]:
        results = []
        for chunk in plan.chunks:
            res = self.fetch_chunk(chunk)
            results.append(res)
        return results

    def fetch_from_fixture(
        self, path: Path, symbol: str, market_scope: MarketScope, interval: str
    ) -> OHLCVFetchResult:
        if not path.exists():
            raise FileNotFoundError(f"Fixture not found: {path}")

        try:
            with open(path) as f:
                payload = json.load(f)
        except json.JSONDecodeError as e:
            raise OHLCVParseError(f"Failed to parse fixture JSON: {e}")

        if not isinstance(payload, list):
            raise OHLCVParseError(f"Fixture payload must be a list, got {type(payload)}")

        bars = parse_kline_payload(
            payload=payload,
            symbol=symbol,
            market_scope=market_scope,
            interval=interval,
            source=OHLCVSource.FIXTURE,
        )

        req = OHLCVFetchRequest(
            symbol=symbol,
            market_scope=market_scope,
            interval=interval,
            start_time_ms=None,
            end_time_ms=None,
            limit=len(bars),
            source=OHLCVSource.FIXTURE,
            request_id=str(uuid.uuid4()),
            correlation_id=str(uuid.uuid4()),
        )

        return OHLCVFetchResult(
            request=req,
            bars=bars,
            response_metadata={"fixture_path": str(path)},
            rate_limit_metadata={},
            success=True,
            error=None,
            fetched_at_utc=datetime.now(UTC).isoformat(),
        )
