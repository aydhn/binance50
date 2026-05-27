from typing import Any

from binance50.core.exceptions import (
    Binance50Error,
    BinanceApiError,
    BinanceAuthenticationError,
    BinanceInsufficientBalanceError,
    BinanceIpBanError,
    BinancePermissionError,
    BinanceRateLimitError,
    BinanceServerError,
    BinanceSymbolFilterError,
    BinanceTimestampError,
    BinanceUnknownExecutionStatusError,
    DivergenceDetectionError,
    FeatureGroupError,
    FeatureMetadataError,
    FeatureQualityError,
    FeatureRegistryError,
    IndicatorV2Error,
    MTFAlignmentError,
    MTFLookaheadError,
    PatternAdapterError,
    PatternEngineError,
    PivotDetectionError,
    RegimeCacheError,
    RegimeClassificationError,
    RegimeConfigError,
    RegimeError,
    RegimeFeatureError,
    RegimeLeakageError,
    RegimeModelAdapterError,
    RegimeQualityError,
    RegimeSmoothingError,
    RegimeStabilityError,
    RegimeTransitionError,
    RegimeValidationError,
    RepaintingRiskError,
    StreamBufferOverflowError,
    StreamConnectionDisabledError,
    StreamDuplicateEventError,
    StreamParseError,
    StreamRouteError,

    MLDatasetError,
    MLDatasetConfigError,
    MLFeatureSourceError,
    MLFeatureSelectionError,
    MLLabelError,
    MLLabelSpecError,
    MLSplitError,
    MLPreprocessingError,
    MLScalerError,
    MLAlignmentError,
    MLLeakageError,
    MLDatasetQualityError,
    MLDatasetRegistryError,
    MLDatasetCacheError,
    MLDatasetExportError,
    StreamStaleEventError,
)


def classify_http_status(
    status_code: int, payload: dict[str, Any] | None = None
) -> type[Binance50Error]:
    """Classify error based on HTTP status code."""
    if status_code == 429:
        return BinanceRateLimitError
    elif status_code == 418:
        return BinanceIpBanError
    elif status_code in (401,):
        return BinanceAuthenticationError
    elif status_code in (403,):
        return BinancePermissionError
    elif 500 <= status_code < 600:
        if status_code in (500, 502, 503, 504):
            # In trading context 5xx means unknown execution status
            return BinanceUnknownExecutionStatusError
        return BinanceServerError
    return BinanceApiError


def classify_binance_error(
    code: int | None, msg: str | None, status_code: int | None = None
) -> type[Binance50Error]:
    """Classify specific binance API error codes and messages."""
    msg_lower = (msg or "").lower()

    if code == -1021 or "timestamp" in msg_lower or "recvwindow" in msg_lower:
        return BinanceTimestampError

    if code == -2010 and "insufficient balance" in msg_lower:
        return BinanceInsufficientBalanceError

    if "min_notional" in msg_lower or "lot_size" in msg_lower or "filter" in msg_lower:
        return BinanceSymbolFilterError

    if status_code is not None:
        return classify_http_status(status_code)

    return BinanceApiError


def is_retryable_error(error: Exception) -> bool:
    """Check if the error is retryable."""
    if isinstance(error, Binance50Error):
        return error.retryable
    return False


def error_to_safe_dict(error: Exception) -> dict[str, Any]:
    """Convert an exception to a safe dictionary representation."""
    from binance50.logging.redaction import redact_text

    if isinstance(error, Binance50Error):
        return error.to_dict(redacted=True)

    return {
        "error_code": "UNHANDLED_EXCEPTION",
        "message": redact_text(str(error)),
        "component": "unknown",
        "severity": "error",
        "retryable": False,
        "user_action_required": False,
        "metadata": {},
        "exception_class": error.__class__.__name__,
    }


def classify_stream_error(msg: str) -> type[Binance50Error]:
    msg_lower = msg.lower()
    if "missing" in msg_lower or "invalid numeric" in msg_lower:
        return StreamParseError
    if "stale" in msg_lower:
        return StreamStaleEventError
    if "duplicate" in msg_lower:
        return StreamDuplicateEventError
    if "overflow" in msg_lower or "buffer full" in msg_lower:
        return StreamBufferOverflowError
    if "route" in msg_lower or "unsupported" in msg_lower:
        return StreamRouteError
    if "real connect disabled" in msg_lower or "disabled in phase 9" in msg_lower:
        return StreamConnectionDisabledError
    from binance50.core.exceptions import StreamError

    return StreamError


def classify_storage_error(error: Exception) -> type[Binance50Error]:
    """Classify storage related errors."""
    from binance50.core.exceptions import (
        DestructiveActionBlockedError,
        ParquetReadError,
        ParquetWriteError,
        SQLiteCatalogError,
        StorageError,
        StorageIntegrityError,
        StoragePathError,
        StorageSchemaError,
    )

    error_str = str(error).lower()
    error_type = error.__class__.__name__

    if "sqlite3" in error_type.lower() or "database error" in error_str:
        return SQLiteCatalogError
    if "pyarrow" in error_type.lower() or "parquet" in error_type.lower():
        if "read" in error_str:
            return ParquetReadError
        return ParquetWriteError
    if "path traversal" in error_str or "outside" in error_str:
        return StoragePathError
    if "schema drift" in error_str or "schema mismatch" in error_str:
        return StorageSchemaError
    if "integrity check failed" in error_str:
        return StorageIntegrityError
    if "destructive action" in error_str or "delete blocked" in error_str:
        return DestructiveActionBlockedError

    return StorageError


def classify_indicator_error(error: Exception) -> type[Binance50Error]:
    from binance50.core.exceptions import (
        IndicatorBackendError,
        IndicatorComputationError,
        IndicatorError,
        IndicatorInputError,
        IndicatorQualityError,
        InsufficientHistoryError,
        LookaheadBiasError,
        OptionalIndicatorBackendMissingError,
    )

    error_str = str(error).lower()

    if "missing ohlcv column" in error_str:
        return IndicatorInputError
    if "invalid backend" in error_str:
        return IndicatorBackendError
    if "optional backend missing" in error_str:
        return OptionalIndicatorBackendMissingError
    if "all nan indicator" in error_str:
        return IndicatorQualityError
    if (
        "future" in error_str
        or "target" in error_str
        or "label" in error_str
        or "lookahead" in error_str
    ):
        return LookaheadBiasError
    if "insufficient rows" in error_str or "insufficient history" in error_str:
        return InsufficientHistoryError
    if isinstance(error, IndicatorError):
        return error.__class__

    return IndicatorComputationError


def classify_indicator_v2_error(exception: Exception) -> str:
    """Classify indicator v2 exceptions to their error codes."""
    import binance50.core.error_codes as error_codes

    if isinstance(exception, RepaintingRiskError):
        return error_codes.REPAINTING_RISK_DETECTED
    elif isinstance(exception, MTFLookaheadError):
        return error_codes.MTF_LOOKAHEAD_DETECTED
    elif isinstance(exception, MTFAlignmentError):
        return error_codes.MTF_ALIGNMENT_FAILED
    elif isinstance(exception, DivergenceDetectionError):
        return error_codes.DIVERGENCE_DETECTION_FAILED
    elif isinstance(exception, PivotDetectionError):
        return error_codes.PIVOT_DETECTION_FAILED
    elif isinstance(exception, FeatureGroupError):
        return error_codes.FEATURE_GROUP_INVALID
    elif isinstance(exception, FeatureMetadataError):
        return error_codes.FEATURE_METADATA_INVALID
    elif isinstance(exception, FeatureRegistryError):
        return error_codes.FEATURE_REGISTRY_FAILED
    elif isinstance(exception, FeatureQualityError):
        return error_codes.FEATURE_QUALITY_FAILED
    elif isinstance(exception, PatternAdapterError):
        return error_codes.PATTERN_ADAPTER_FAILED
    elif isinstance(exception, PatternEngineError):
        return error_codes.PATTERN_ENGINE_FAILED
    elif isinstance(exception, IndicatorV2Error):
        return error_codes.INDICATOR_V2_FAILED
    return "UNKNOWN_ERROR"


def classify_strategy_error(error: Exception) -> type[Binance50Error]:
    from binance50.core.exceptions import (
        ActionableLanguageDetectedError,
        ExecutionObjectDetectedError,
        StrategyCandidateError,
        StrategyConfigError,
        StrategyError,
        StrategyExplanationError,
        StrategyInputError,
        StrategyPluginError,
    )

    error_str = str(error).lower()

    if "missing required feature" in error_str:
        return StrategyInputError
    if "order language" in error_str or "actionable language" in error_str:
        return ActionableLanguageDetectedError
    if "execution object" in error_str:
        return ExecutionObjectDetectedError
    if "confidence" in error_str and "out of range" in error_str:
        return StrategyCandidateError
    if "missing explanation" in error_str:
        return StrategyExplanationError
    if "unsafe config" in error_str:
        return StrategyConfigError

    if isinstance(error, StrategyError):
        return error.__class__

    return StrategyPluginError


def classify_regime_error(error: Exception) -> type[Binance50Error]:
    if isinstance(error, RegimeError):
        return type(error)

    error_msg = str(error).lower()
    if (
        "future" in error_msg
        or "target" in error_msg
        or "label" in error_msg
        or "centered" in error_msg
        or "train split missing" in error_msg
        or "train split required" in error_msg
        or "full dataset fit" in error_msg
    ):
        return RegimeLeakageError
    elif "feature" in error_msg:
        return RegimeFeatureError
    elif "confidence out of range" in error_msg:
        return RegimeValidationError
    elif "missing explanation" in error_msg or "transition ratio" in error_msg:
        return RegimeQualityError
    elif "adapter" in error_msg:
        return RegimeModelAdapterError
    elif "config" in error_msg:
        return RegimeConfigError
    elif "cache" in error_msg:
        return RegimeCacheError
    elif "stability" in error_msg:
        return RegimeStabilityError
    elif "transition" in error_msg:
        return RegimeTransitionError
    elif "smoothing" in error_msg:
        return RegimeSmoothingError
    elif "validation" in error_msg:
        return RegimeValidationError

    return RegimeClassificationError


def classify_backtest_error(message: str) -> type[Exception]:
    from binance50.core.exceptions import (
        BacktestError,
        BacktestExecutionForbiddenError,
        BacktestLeakageError,
        BacktestMetricError,
        BacktestOrderIdentifierDetectedError,
        BacktestPortfolioError,
        BacktestQualityError,
        SameBarFillError,
    )

    if "same bar fill" in message.lower():
        return SameBarFillError
    elif "future column" in message.lower() or "centered rolling" in message.lower():
        return BacktestLeakageError
    elif "exchange order id" in message.lower():
        return BacktestOrderIdentifierDetectedError
    elif "signed request payload" in message.lower():
        return BacktestExecutionForbiddenError
    elif "invalid metric" in message.lower():
        return BacktestMetricError
    elif "invalid equity" in message.lower():
        return BacktestPortfolioError
    elif "quality fail" in message.lower():
        return BacktestQualityError
    return BacktestError

def is_ml_training_error(error: Exception) -> bool:
    from binance50.core.exceptions import MLTrainingError
    return isinstance(error, MLTrainingError)

def classify_ml_error(error_message: str) -> str:
    from binance50.core.error_codes import ErrorCode
    msg = error_message.lower()
    if "leakage" in msg or "future" in msg or "target" in msg:
        return ErrorCode.ML_MODEL_LEAKAGE_DETECTED
    if "single class" in msg:
        return ErrorCode.ML_TARGET_INVALID
    if "fit error" in msg:
        return ErrorCode.ML_ESTIMATOR_FAILED
    if "nan" in msg or "inf" in msg:
        return ErrorCode.ML_METRICS_FAILED
    if "calibration fit on test" in msg:
        return ErrorCode.ML_CALIBRATION_FAILED
    if "missing model card" in msg:
        return ErrorCode.ML_MODEL_CARD_FAILED
    if "serving promotion attempt" in msg:
        return ErrorCode.ML_SERVING_FORBIDDEN
    if "untrusted artifact load" in msg:
        return ErrorCode.ML_MODEL_ARTIFACT_FAILED
    return ErrorCode.ML_TRAINING_CONFIG_INVALID

def is_ml_inference_error(error: Exception) -> bool:
    from binance50.core.exceptions import MLInferenceError
    return isinstance(error, MLInferenceError)

def classify_ml_inference_error(error_message: str) -> str:
    from binance50.core.error_codes import (
        ML_ARTIFACT_UNTRUSTED,
        ML_ARTIFACT_HASH_MISMATCH,
        ML_FEATURE_SCHEMA_INVALID,
        ML_INFERENCE_PREPROCESSING_FAILED,
        ML_PROBABILITY_INVALID,
        ML_CALIBRATION_CHECK_FAILED,
        ML_SIGNAL_INTEGRATION_FORBIDDEN,
        ML_SERVING_FORBIDDEN,
        ML_INFERENCE_QUALITY_FAILED,
        ML_INFERENCE_CONFIG_INVALID
    )
    msg = error_message.lower()

    if "untrusted artifact" in msg or "manual artifact path" in msg:
        return ML_ARTIFACT_UNTRUSTED
    if "hash mismatch" in msg:
        return ML_ARTIFACT_HASH_MISMATCH
    if "feature schema mismatch" in msg or "extra feature" in msg or "missing feature" in msg:
        return ML_FEATURE_SCHEMA_INVALID
    if "inference fit attempt" in msg:
        return ML_INFERENCE_PREPROCESSING_FAILED
    if "probability out of range" in msg or "probability sum invalid" in msg:
        return ML_PROBABILITY_INVALID
    if "calibration check failure" in msg:
        return ML_CALIBRATION_CHECK_FAILED
    if "production signal write attempt" in msg:
        return ML_SIGNAL_INTEGRATION_FORBIDDEN
    if "serving attempt" in msg:
        return ML_SERVING_FORBIDDEN
    if "quality fail" in msg:
        return ML_INFERENCE_QUALITY_FAILED

    return ML_INFERENCE_CONFIG_INVALID
