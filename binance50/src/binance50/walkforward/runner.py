import uuid
from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.walkforward.degradation import (
    compute_degradation_for_all_windows,
    summarize_degradation,
)
from binance50.walkforward.fixed_params import run_fixed_params_for_window
from binance50.walkforward.models import (
    WalkForwardMode,
    WalkForwardRunRequest,
    WalkForwardRunResult,
    WalkForwardWindow,
    WalkForwardWindowResult,
    WalkForwardWindowStatus,
)
from binance50.walkforward.oos import run_oos_backtest_for_window
from binance50.walkforward.parameter_drift import (
    compute_parameter_drift_series,
    summarize_parameter_drift,
)
from binance50.walkforward.quality import build_walkforward_quality_report
from binance50.walkforward.regime_analysis import build_walkforward_regime_report
from binance50.walkforward.reproducibility import compute_walkforward_output_hash
from binance50.walkforward.robustness import compute_walkforward_robustness
from binance50.walkforward.splitters import apply_embargo_and_gaps, slice_window_data
from binance50.walkforward.stability import compute_walkforward_stability
from binance50.walkforward.stitching import stitch_oos_equity
from binance50.walkforward.windows import build_walkforward_windows


class WalkForwardRunner:
    def __init__(
        self,
        config: AppConfig,
        data_loader: Any = None,
        window_builder: Any = None,
        optimizer_bridge: Any = None,
        fixed_param_runner: Any = None,
        backtest_runner: Any = None,
        report_pack_builder: Any = None,
        storage: Any = None,
    ):
        self.config = config
        self.data_loader = data_loader
        self.window_builder = window_builder or build_walkforward_windows
        self.optimizer_bridge = optimizer_bridge
        self.fixed_param_runner = fixed_param_runner or run_fixed_params_for_window
        self.backtest_runner = backtest_runner
        self.report_pack_builder = report_pack_builder
        self.storage = storage

    def run(self, request: WalkForwardRunRequest, df: Any) -> WalkForwardRunResult:
        run_id = str(uuid.uuid4())

        # 1. Build window plan
        windows = self.window_builder(df, self.config)
        window_results: dict[str, WalkForwardWindowResult] = {}

        # 2. Process each window
        for window in windows:
            try:
                # 2.a Data Split & Embargo
                train_df, val_df, test_df = slice_window_data(df, window)
                train_df, val_df, test_df = apply_embargo_and_gaps(df, window, self.config)

                # 2.b Train / Validate
                win_result = self.process_window(window, train_df, val_df, test_df, request)
                window_results[window.window_id] = win_result
            except Exception as e:
                window_results[window.window_id] = WalkForwardWindowResult(
                    window_id=window.window_id, status=WalkForwardWindowStatus.failed, error=str(e)
                )
                if not self.config.walkforward.mode.continue_on_window_failure:
                    break

        # 3. Post-processing
        stitched_equity = stitch_oos_equity(window_results, self.config)
        drift_reports = compute_parameter_drift_series(window_results, self.config)
        drift_summary = summarize_parameter_drift(drift_reports, self.config)
        deg_reports = compute_degradation_for_all_windows(window_results, self.config)
        deg_summary = summarize_degradation(deg_reports, self.config)
        stability_report = compute_walkforward_stability(window_results, drift_reports, self.config)
        regime_report = build_walkforward_regime_report(window_results, self.config)
        robustness_report = compute_walkforward_robustness(
            window_results, stability_report, deg_reports, drift_reports, self.config
        )

        result = WalkForwardRunResult(
            request=request,
            run_id=run_id,
            mode=request.mode,
            windows=windows,
            window_results=window_results,
            stitched_oos_equity=stitched_equity,
            aggregate_oos_metrics={"mock": "data"},
            stability_report=stability_report.model_dump(),
            degradation_summary=deg_summary,
            parameter_drift_summary=drift_summary,
            regime_summary=regime_report.model_dump(),
            robustness_report=robustness_report.model_dump(),
            quality_report={},
            success=True,
        )

        quality_report = build_walkforward_quality_report(result, self.config)
        result.quality_report = quality_report.model_dump()
        result.metadata["output_hash"] = compute_walkforward_output_hash(result)
        result.success = quality_report.status != "failed"

        return result

    def process_window(
        self,
        window: WalkForwardWindow,
        train_df: Any,
        validation_df: Any,
        test_df: Any,
        request: WalkForwardRunRequest,
    ) -> WalkForwardWindowResult:
        if self.config.walkforward.mode.run_optimizer_per_window and self.optimizer_bridge:
            res = self.run_optimizer_window(window, train_df, validation_df, test_df, request)
        else:
            res = self.run_fixed_params_window(window, train_df, validation_df, test_df, request)

        # OOS Phase
        if res.status == WalkForwardWindowStatus.completed and res.selected_parameter_set:
            res = self.run_oos_window(res, window, test_df, request)

        return res

    def run_optimizer_window(
        self,
        window: WalkForwardWindow,
        train_df: Any,
        validation_df: Any,
        test_df: Any,
        request: WalkForwardRunRequest,
    ) -> WalkForwardWindowResult:
        opt_res = self.optimizer_bridge.run_optimizer_for_window(
            window, train_df, validation_df, request
        )
        best_trial = self.optimizer_bridge.select_best_trial_for_window(opt_res, self.config)

        return WalkForwardWindowResult(
            window_id=window.window_id,
            status=WalkForwardWindowStatus.completed
            if best_trial
            else WalkForwardWindowStatus.failed,
            optimizer_result=opt_res,
            selected_trial=best_trial,
            selected_parameter_set=getattr(best_trial, "parameters", {}) if best_trial else None,
        )

    def run_fixed_params_window(
        self,
        window: WalkForwardWindow,
        train_df: Any,
        validation_df: Any,
        test_df: Any,
        request: WalkForwardRunRequest,
    ) -> WalkForwardWindowResult:
        return self.fixed_param_runner(
            window, train_df, validation_df, test_df, request, self.config
        )

    def run_oos_window(
        self,
        win_result: WalkForwardWindowResult,
        window: WalkForwardWindow,
        test_df: Any,
        request: WalkForwardRunRequest,
    ) -> WalkForwardWindowResult:
        bt_res, rp = run_oos_backtest_for_window(
            window,
            win_result.selected_parameter_set,
            test_df,
            request,
            self.backtest_runner,
            self.report_pack_builder,
            self.config,
        )
        win_result.oos_backtest_result = bt_res
        win_result.oos_report = {"metrics": rp.metrics} if hasattr(rp, "metrics") else {}
        return win_result

    def run_from_fixture(
        self, fixture_name: str, symbol: str, market_scope: str, interval: str
    ) -> WalkForwardRunResult:
        # Mocking data load
        df = pd.DataFrame({"equity": [1000] * 10000})  # sufficient size
        req = WalkForwardRunRequest(
            symbol=symbol,
            market_scope=market_scope,
            interval=interval,
            input_ohlcv_dataset_name=fixture_name,
            mode=WalkForwardMode(self.config.walkforward.mode.default_mode),
            optimizer_method="grid",
            request_id="req1",
            correlation_id="corr1",
        )
        return self.run(req, df)

    def run_from_warehouse(
        self,
        symbol: str,
        market_scope: str,
        interval: str,
        start_time_ms: int = None,
        end_time_ms: int = None,
    ) -> WalkForwardRunResult:
        pass
