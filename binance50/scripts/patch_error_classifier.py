from pathlib import Path

file_path = Path("src/binance50/core/error_classifier.py")
content = file_path.read_text()

error_classifier = """
def classify_indicator_error(error: Exception) -> type[Binance50Error]:
    from binance50.core.exceptions import (
        IndicatorError, IndicatorInputError, IndicatorBackendError,
        OptionalIndicatorBackendMissingError, IndicatorQualityError,
        LookaheadBiasError, InsufficientHistoryError, IndicatorComputationError
    )

    error_str = str(error).lower()
    error_type = error.__class__.__name__

    if "missing ohlcv column" in error_str:
        return IndicatorInputError
    if "invalid backend" in error_str:
        return IndicatorBackendError
    if "optional backend missing" in error_str:
        return OptionalIndicatorBackendMissingError
    if "all nan indicator" in error_str:
        return IndicatorQualityError
    if "future" in error_str or "target" in error_str or "label" in error_str or "lookahead" in error_str:
        return LookaheadBiasError
    if "insufficient rows" in error_str or "insufficient history" in error_str:
        return InsufficientHistoryError
    if isinstance(error, IndicatorError):
        return error.__class__

    return IndicatorComputationError
"""

if "def classify_indicator_error" not in content:
    content += "\n" + error_classifier

file_path.write_text(content)
print("Patched error classifier")
