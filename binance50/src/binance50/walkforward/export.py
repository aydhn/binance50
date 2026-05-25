from pathlib import Path

from binance50.walkforward.models import WalkForwardRunResult


def export_walkforward_summary_to_json(result: WalkForwardRunResult, path: Path) -> None:
    pass


def export_window_results_to_csv(result: WalkForwardRunResult, path: Path) -> None:
    pass


def export_oos_equity_to_csv(result: WalkForwardRunResult, path: Path) -> None:
    pass


def export_parameter_drift_to_json(result: WalkForwardRunResult, path: Path) -> None:
    pass


def export_degradation_to_json(result: WalkForwardRunResult, path: Path) -> None:
    pass


def export_stability_to_json(result: WalkForwardRunResult, path: Path) -> None:
    pass


def export_robustness_to_json(result: WalkForwardRunResult, path: Path) -> None:
    pass


def export_walkforward_report_to_markdown(result: WalkForwardRunResult, path: Path) -> None:
    pass
