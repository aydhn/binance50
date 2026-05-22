from pathlib import Path

file_path = Path("src/binance50/core/exceptions.py")
content = file_path.read_text()

exceptions = """
# Phase 11 Indicator Exceptions
class IndicatorError(Binance50Error):
    pass

class IndicatorConfigError(IndicatorError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.INDICATOR_CONFIG_INVALID)
        super().__init__(message, **kwargs)

class IndicatorInputError(IndicatorError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.INDICATOR_INPUT_INVALID)
        super().__init__(message, **kwargs)

class IndicatorValidationError(IndicatorError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.INDICATOR_VALIDATION_FAILED)
        super().__init__(message, **kwargs)

class IndicatorComputationError(IndicatorError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.INDICATOR_COMPUTATION_FAILED)
        super().__init__(message, **kwargs)

class IndicatorRegistryError(IndicatorError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.INDICATOR_REGISTRY_FAILED)
        super().__init__(message, **kwargs)

class IndicatorBackendError(IndicatorError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.INDICATOR_BACKEND_FAILED)
        super().__init__(message, **kwargs)

class OptionalIndicatorBackendMissingError(IndicatorError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.OPTIONAL_INDICATOR_BACKEND_MISSING)
        super().__init__(message, **kwargs)

class IndicatorQualityError(IndicatorError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.INDICATOR_QUALITY_FAILED)
        super().__init__(message, **kwargs)

class IndicatorCacheError(IndicatorError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.INDICATOR_CACHE_FAILED)
        super().__init__(message, **kwargs)

class LookaheadBiasError(IndicatorError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.LOOKAHEAD_BIAS_DETECTED)
        super().__init__(message, **kwargs)

class InsufficientHistoryError(IndicatorError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.INSUFFICIENT_HISTORY)
        super().__init__(message, **kwargs)

class WarmupError(IndicatorError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.WARMUP_FAILED)
        super().__init__(message, **kwargs)
"""

if "class IndicatorError" not in content:
    content += "\n" + exceptions

file_path.write_text(content)
print("Patched exceptions")
