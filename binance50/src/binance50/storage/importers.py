from typing import Any

from binance50.config.models import AppConfig
from binance50.walkforward.models import WalkForwardRunResult
from binance50.walkforward.validators import validate_no_live_or_paper_intent


def import_walkforward_result(result: WalkForwardRunResult, config: AppConfig) -> Any:
    validate_no_live_or_paper_intent(getattr(result, "request", {}))

    # Dummy manifest implementation
    class DatasetManifest:
        pass

    return DatasetManifest()
