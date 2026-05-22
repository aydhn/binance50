import hashlib
import json
import time
from datetime import UTC, datetime

import pandas as pd

from binance50.config.models import AppConfig
from binance50.core.enums import MarketScope
from binance50.core.exceptions import IndicatorComputationError
from binance50.indicators.adapters.base import IndicatorBackendAdapter
from binance50.indicators.context import build_indicator_context
from binance50.indicators.models import (
    IndicatorBackend,
    IndicatorFrameMetadata,
    IndicatorRunRequest,
    IndicatorRunResult,
)
from binance50.indicators.quality import (
    assert_indicator_quality_passed,
    build_indicator_quality_report,
)
from binance50.indicators.registry import IndicatorRegistry
from binance50.indicators.validators import validate_indicator_output, validate_ohlcv_input
from binance50.indicators.warmup import (
    assert_sufficient_history,
    estimate_max_lookback,
    mark_warmup_rows,
    summarize_warmup,
)
from binance50.safety.indicator_guard import (
    assert_indicator_input_safe,
    assert_indicator_output_safe,
)


class IndicatorEngine:
    def __init__(self, config: AppConfig, registry: IndicatorRegistry, adapter: IndicatorBackendAdapter):
        self.config = config
        self.registry = registry
        self.adapter = adapter

    def compute(self, df: pd.DataFrame, request: IndicatorRunRequest) -> IndicatorRunResult:
        time.time()

        try:
            # 1. Validate Input
            assert_indicator_input_safe(df, self.config)
            validate_ohlcv_input(df, self.config)

            # Drop incomplete candle if config says so and it's the last row
            if self.config.indicators.drop_incomplete_last_candle and "is_closed" in df.columns:
                if not df["is_closed"].iloc[-1]:
                    df = df.iloc[:-1]

            # 2. Check History & Lookback
            specs = request.indicator_specs
            if not specs:
                specs = self.registry.list_specs(backend=IndicatorBackend(request.backend))

            self.registry.validate_specs(specs, self.config)
            assert_sufficient_history(df, specs, self.config)

            max_lookback = estimate_max_lookback(specs)
            df = mark_warmup_rows(df, max_lookback)

            # 3. Process Specs
            output_columns = []

            for spec in specs:
                ctx = build_indicator_context(
                    self.config, request.symbol, request.market_scope,
                    request.interval, request.backend, spec.input_columns, request.correlation_id
                )

                try:
                    res_df = self.adapter.compute(spec, df, ctx)
                    # We expect res_df to have same index as df
                    for col in res_df.columns:
                        df[col] = res_df[col]
                        output_columns.append(col)
                except Exception as e:
                    raise IndicatorComputationError(f"Failed to compute {spec.name}: {e}") from e

            # 4. Fill policy
            if self.config.indicators.fill_policy == "ffill":
                df[output_columns] = df[output_columns].ffill()
            elif self.config.indicators.fill_policy == "zero":
                df[output_columns] = df[output_columns].fillna(0.0)

            # 5. Output Validation & Quality
            assert_indicator_output_safe(df, self.config)
            validate_indicator_output(df, self.config)

            quality = build_indicator_quality_report(df, output_columns, self.config)
            assert_indicator_quality_passed(quality, self.config)

            # 6. Metadata
            warmup_summary = summarize_warmup(df, output_columns, max_lookback)

            # Compute hashes
            input_hash = hashlib.sha256(pd.util.hash_pandas_object(df[["open_time", "close"]]).values).hexdigest()
            output_hash = hashlib.sha256(pd.util.hash_pandas_object(df[output_columns]).values).hexdigest()
            config_hash = hashlib.sha256(json.dumps(request.to_dict(), sort_keys=True).encode()).hexdigest()

            start_open = int(df["open_time"].min())
            end_open = int(df["open_time"].max())

            meta = IndicatorFrameMetadata(
                symbol=request.symbol,
                market_scope=request.market_scope,
                interval=request.interval,
                backend=request.backend,
                row_count=len(df),
                input_row_count=len(df),
                indicator_count=len(output_columns),
                start_open_time=start_open,
                end_open_time=end_open,
                max_lookback=max_lookback,
                warmup_rows=warmup_summary["warmup_rows"],
                valid_rows=warmup_summary["valid_rows"],
                generated_at_utc=datetime.now(UTC).isoformat(),
                input_hash=input_hash,
                output_hash=output_hash,
                config_hash=config_hash
            )

            # Drop input columns if requested
            if not request.include_input_columns:
                df = df[["open_time", "close_time", "is_warmup"] + output_columns]

            return IndicatorRunResult(request, df, meta, quality, success=True)

        except Exception as e:
            from binance50.core.error_classifier import classify_indicator_error
            classify_indicator_error(e)
            return IndicatorRunResult(request, pd.DataFrame(), None, None, False, str(e))

    def compute_default(self, df: pd.DataFrame, symbol: str, market_scope: MarketScope, interval: str) -> IndicatorRunResult:
        req = IndicatorRunRequest(
            symbol=symbol,
            market_scope=market_scope,
            interval=interval,
            input_dataset_name="ohlcv",
            backend=self.config.indicators.default_backend,
            indicator_specs=[]
        )
        return self.compute(df, req)
