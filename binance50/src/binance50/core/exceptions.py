from typing import Any

from binance50.core import error_codes


class Binance50Error(Exception):
    def __init__(self, message: str, **kwargs: Any) -> None:
        self.message = message
        self.error_code = kwargs.get("error_code", "UNKNOWN_ERROR")
        self.component = kwargs.get("component", "unknown")
        self.severity = kwargs.get("severity", "error")
        self.retryable = kwargs.get("retryable", False)
        self.user_action_required = kwargs.get("user_action_required", False)
        self.metadata = kwargs.get("metadata", {})
        super().__init__(self.message)

    def with_context(self, **kwargs: Any) -> "Binance50Error":
        self.metadata.update(kwargs)
        return self

    def safe_message(self) -> str:
        from binance50.logging.redaction import redact_text

        return redact_text(self.message)

    def to_dict(self, redacted: bool = True) -> dict[str, Any]:
        d = {
            "error_code": self.error_code,
            "message": self.safe_message() if redacted else self.message,
            "component": self.component,
            "severity": self.severity,
            "retryable": self.retryable,
            "user_action_required": self.user_action_required,
            "exception_class": self.__class__.__name__,
            "metadata": self.metadata.copy(),
        }
        if redacted:
            from binance50.logging.redaction import redact_mapping

            d["metadata"] = redact_mapping(d["metadata"])
        return d


class ConfigError(Binance50Error):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.CONFIG_LOAD_FAILED)
        kwargs.setdefault("component", "config")
        super().__init__(message, **kwargs)


class ConfigValidationError(ConfigError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.CONFIG_VALIDATION_FAILED)
        super().__init__(message, **kwargs)


class EnvironmentProfileError(Binance50Error):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.ENVIRONMENT_PROFILE_INVALID)
        kwargs.setdefault("component", "environment")
        super().__init__(message, **kwargs)


class SafetyError(Binance50Error):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.SAFETY_CHECK_FAILED)
        kwargs.setdefault("component", "safety")
        kwargs.setdefault("severity", "critical")
        super().__init__(message, **kwargs)


class SecretLeakError(SafetyError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.SECRET_LEAK_DETECTED)
        super().__init__(message, **kwargs)


class LiveTradingBlockedError(SafetyError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.LIVE_TRADING_BLOCKED)
        super().__init__(message, **kwargs)


class InvalidTradingModeError(SafetyError):
    pass


class LoggingSetupError(Binance50Error):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.LOGGING_SETUP_FAILED)
        kwargs.setdefault("component", "logging")
        super().__init__(message, **kwargs)


class AuditWriteError(Binance50Error):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.AUDIT_WRITE_FAILED)
        kwargs.setdefault("component", "audit")
        super().__init__(message, **kwargs)


class DataValidationError(Binance50Error):
    pass


class DependencyMissingError(Binance50Error):
    pass


class UnsupportedFeatureError(Binance50Error):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.UNSUPPORTED_FEATURE)
        super().__init__(message, **kwargs)


class StateError(Binance50Error):
    pass


class RuntimeInvariantError(Binance50Error):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.RUNTIME_INVARIANT_FAILED)
        super().__init__(message, **kwargs)


class BinanceApiError(Binance50Error):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("component", "binance_api")
        super().__init__(message, **kwargs)


class BinanceRateLimitError(BinanceApiError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.BINANCE_RATE_LIMIT)
        kwargs.setdefault("retryable", True)
        super().__init__(message, **kwargs)


class BinanceIpBanError(BinanceApiError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.BINANCE_IP_BAN)
        kwargs.setdefault("severity", "critical")
        kwargs.setdefault("user_action_required", True)
        super().__init__(message, **kwargs)


class BinanceRequestError(BinanceApiError):
    pass


class BinanceServerError(BinanceApiError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.BINANCE_SERVER_ERROR)
        kwargs.setdefault("retryable", True)
        super().__init__(message, **kwargs)


class BinanceUnknownExecutionStatusError(BinanceApiError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.BINANCE_UNKNOWN_EXECUTION_STATUS)
        kwargs.setdefault("severity", "critical")
        kwargs.setdefault("user_action_required", True)
        super().__init__(message, **kwargs)


class BinanceAuthenticationError(BinanceApiError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.BINANCE_AUTH_FAILED)
        kwargs.setdefault("severity", "critical")
        kwargs.setdefault("user_action_required", True)
        super().__init__(message, **kwargs)


class BinancePermissionError(BinanceApiError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.BINANCE_PERMISSION_DENIED)
        kwargs.setdefault("severity", "critical")
        kwargs.setdefault("user_action_required", True)
        super().__init__(message, **kwargs)


class BinanceTimestampError(BinanceApiError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.BINANCE_TIMESTAMP_ERROR)
        kwargs.setdefault("retryable", True)
        super().__init__(message, **kwargs)


class BinanceInsufficientBalanceError(BinanceApiError):
    pass


class BinanceOrderRejectedError(BinanceApiError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.BINANCE_ORDER_REJECTED)
        super().__init__(message, **kwargs)


class BinanceSymbolFilterError(BinanceApiError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.BINANCE_SYMBOL_FILTER_FAILED)
        super().__init__(message, **kwargs)


class BinanceWebSocketError(BinanceApiError):
    pass


class BinanceUserDataStreamError(BinanceApiError):
    pass


class CredentialError(Binance50Error):
    pass


class CredentialPairError(CredentialError):
    default_code = "CREDENTIAL_PAIR_INCOMPLETE"


class ApiPermissionError(Binance50Error):
    default_code = "API_PERMISSION_INVALID"


class DryRunViolationError(SafetyError):
    default_code = "DRY_RUN_VIOLATION"


class OrderPathDisabledError(SafetyError):
    default_code = "ORDER_PATH_DISABLED"


class UnsafeConfigurationError(SafetyError):
    default_code = "UNSAFE_CONFIGURATION"


class GitIgnorePolicyError(SafetyError):
    default_code = "GITIGNORE_ENV_MISSING"


class EnvFilePolicyError(SafetyError):
    default_code = "ENV_EXAMPLE_SECRET_DETECTED"


class LiveUnlockError(SafetyError):
    default_code = "LIVE_UNLOCK_MISSING"


class UnsupportedPermissionError(ApiPermissionError):
    default_code = "UNSUPPORTED_PERMISSION"


class ConnectorDisabledError(UnsupportedFeatureError):
    def __init__(self, message: str = "Connector is disabled", **kwargs: Any) -> None:
        super().__init__(message, **kwargs)


class RateLimitError(Binance50Error):
    pass


class RateLimitExceededError(RateLimitError):
    pass


class RateLimitCooldownError(RateLimitError):
    pass


class IpBanCooldownError(RateLimitError):
    pass


class RetryPolicyError(Binance50Error):
    pass


class BackoffPolicyError(Binance50Error):
    pass


class TimeoutPolicyError(Binance50Error):
    pass


class ClockSyncError(Binance50Error):
    pass


class ClockDriftError(ClockSyncError):
    pass


class RecvWindowError(Binance50Error):
    pass


class CircuitBreakerOpenError(Binance50Error):
    pass


class WebSocketLimitError(Binance50Error):
    pass


class RequestBudgetError(Binance50Error):
    pass


class RealNetworkDisabledError(SafetyError):
    pass


class MarketDataError(Binance50Error):
    pass


class MarketDataFetchDisabledError(MarketDataError):
    pass


class OHLCVParseError(MarketDataError):
    pass


class OHLCVValidationError(MarketDataError):
    pass


class OHLCVQualityError(MarketDataError):
    pass


class OHLCVCacheError(MarketDataError):
    pass


class OHLCVStoreError(MarketDataError):
    pass


class OHLCVIncrementalError(MarketDataError):
    pass


class FetchPlanError(MarketDataError):
    pass


class UnsupportedIntervalError(MarketDataError):
    pass


class IncompleteCandleError(MarketDataError):
    pass


class DataGapError(MarketDataError):
    pass


# Phase 9 Stream Exceptions
class StreamError(Binance50Error):
    pass


class StreamConfigError(StreamError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STREAM_CONFIG_INVALID)
        super().__init__(message, **kwargs)


class StreamConnectionDisabledError(StreamError):
    def __init__(
        self, message: str = "Real WebSocket connections are disabled in Phase 9", **kwargs: Any
    ) -> None:
        kwargs.setdefault("error_code", error_codes.STREAM_REAL_CONNECT_DISABLED)
        super().__init__(message, **kwargs)


class StreamSubscriptionError(StreamError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STREAM_SUBSCRIPTION_INVALID)
        super().__init__(message, **kwargs)


class StreamParseError(StreamError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STREAM_PARSE_FAILED)
        super().__init__(message, **kwargs)


class StreamValidationError(StreamError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STREAM_VALIDATION_FAILED)
        super().__init__(message, **kwargs)


class StreamBufferOverflowError(StreamError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STREAM_BUFFER_OVERFLOW)
        super().__init__(message, **kwargs)


class StreamDuplicateEventError(StreamError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STREAM_DUPLICATE_EVENT)
        super().__init__(message, **kwargs)


class StreamStaleEventError(StreamError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STREAM_STALE_EVENT)
        super().__init__(message, **kwargs)


class StreamOutOfOrderError(StreamError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STREAM_OUT_OF_ORDER)
        super().__init__(message, **kwargs)


class StreamReplayError(StreamError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STREAM_REPLAY_FAILED)
        super().__init__(message, **kwargs)


class StreamRouteError(StreamError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STREAM_ROUTE_INVALID)
        super().__init__(message, **kwargs)


class StreamLifecycleError(StreamError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STREAM_LIFECYCLE_INVALID)
        super().__init__(message, **kwargs)


class RealtimeStoreError(Binance50Error):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.REALTIME_STORE_FAILED)
        super().__init__(message, **kwargs)


# Phase 10 Storage Exceptions
class StorageError(Binance50Error):
    pass


class StorageConfigError(StorageError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STORAGE_CONFIG_INVALID)
        super().__init__(message, **kwargs)


class StoragePathError(StorageError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STORAGE_PATH_INVALID)
        super().__init__(message, **kwargs)


class StorageSchemaError(StorageError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STORAGE_SCHEMA_INVALID)
        super().__init__(message, **kwargs)


class StorageCatalogError(StorageError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STORAGE_CATALOG_FAILED)
        super().__init__(message, **kwargs)


class StorageMigrationError(StorageError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STORAGE_MIGRATION_FAILED)
        super().__init__(message, **kwargs)


class StorageIntegrityError(StorageError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STORAGE_INTEGRITY_FAILED)
        super().__init__(message, **kwargs)


class StorageManifestError(StorageError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STORAGE_MANIFEST_INVALID)
        super().__init__(message, **kwargs)


class StoragePartitionError(StorageError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STORAGE_PARTITION_INVALID)
        super().__init__(message, **kwargs)


class StorageBackupError(StorageError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STORAGE_BACKUP_FAILED)
        super().__init__(message, **kwargs)


class StorageRetentionError(StorageError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STORAGE_RETENTION_FAILED)
        super().__init__(message, **kwargs)


class StorageLockError(StorageError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STORAGE_LOCK_FAILED)
        super().__init__(message, **kwargs)


class DatasetRegistryError(StorageError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.DATASET_REGISTRY_FAILED)
        super().__init__(message, **kwargs)


class DataIndexError(StorageError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.DATA_INDEX_FAILED)
        super().__init__(message, **kwargs)


class QualityIndexError(StorageError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.QUALITY_INDEX_FAILED)
        super().__init__(message, **kwargs)


class ParquetWriteError(StorageError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.PARQUET_WRITE_FAILED)
        super().__init__(message, **kwargs)


class ParquetReadError(StorageError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.PARQUET_READ_FAILED)
        super().__init__(message, **kwargs)


class SQLiteCatalogError(StorageError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.SQLITE_CATALOG_FAILED)
        super().__init__(message, **kwargs)


class DestructiveActionBlockedError(SafetyError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.DESTRUCTIVE_ACTION_BLOCKED)
        super().__init__(message, **kwargs)


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


class IndicatorV2Error(Binance50Error):
    """Base exception for Indicator V2 related errors."""

    pass


class PivotDetectionError(IndicatorV2Error):
    """Raised when pivot detection fails."""

    pass


class DivergenceDetectionError(IndicatorV2Error):
    """Raised when divergence detection fails."""

    pass


class MTFAlignmentError(IndicatorV2Error):
    """Raised when MTF alignment fails."""

    pass


class MTFLookaheadError(MTFAlignmentError):
    """Raised when MTF alignment attempts to use future data."""

    pass


class FeatureGroupError(IndicatorV2Error):
    """Raised when feature grouping fails or is invalid."""

    pass


class FeatureMetadataError(IndicatorV2Error):
    """Raised when feature metadata is invalid."""

    pass


class FeatureRegistryError(IndicatorV2Error):
    """Raised when operations on the feature registry fail."""

    pass


class FeatureQualityError(IndicatorV2Error):
    """Raised when feature quality checks fail."""

    pass


class PatternEngineError(IndicatorV2Error):
    """Raised when pattern engine operations fail."""

    pass


class PatternAdapterError(PatternEngineError):
    """Raised when pattern adapters fail or are missing."""

    pass


class RepaintingRiskError(IndicatorV2Error):
    """Raised when a repainting risk is detected in indicator parameters."""

    pass


# Phase 13 Strategy Exceptions
class StrategyError(Binance50Error):
    pass


class StrategyConfigError(StrategyError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STRATEGY_CONFIG_INVALID)
        super().__init__(message, **kwargs)


class StrategyPluginError(StrategyError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STRATEGY_PLUGIN_FAILED)
        super().__init__(message, **kwargs)


class StrategyRegistryError(StrategyError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STRATEGY_REGISTRY_FAILED)
        super().__init__(message, **kwargs)


class StrategyInputError(StrategyError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STRATEGY_INPUT_INVALID)
        super().__init__(message, **kwargs)


class StrategyValidationError(StrategyError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STRATEGY_VALIDATION_FAILED)
        super().__init__(message, **kwargs)


class StrategyCandidateError(StrategyError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STRATEGY_CANDIDATE_INVALID)
        super().__init__(message, **kwargs)


class StrategyExplanationError(StrategyError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STRATEGY_EXPLANATION_INVALID)
        super().__init__(message, **kwargs)


class StrategyQualityError(StrategyError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STRATEGY_QUALITY_FAILED)
        super().__init__(message, **kwargs)


class StrategyCacheError(StrategyError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.STRATEGY_CACHE_FAILED)
        super().__init__(message, **kwargs)


class OrderIntentForbiddenError(StrategyError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.ORDER_INTENT_FORBIDDEN)
        super().__init__(message, **kwargs)


class ExecutionObjectDetectedError(StrategyError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.EXECUTION_OBJECT_DETECTED)
        super().__init__(message, **kwargs)


class ActionableLanguageDetectedError(StrategyError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.ACTIONABLE_LANGUAGE_DETECTED)
        super().__init__(message, **kwargs)


class RuntimeInvariantFailedError(Binance50Error):
    pass


# Phase 14 Signal Exceptions
class SignalError(Binance50Error):
    pass


class SignalConfigError(SignalError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.SIGNAL_CONFIG_INVALID)
        super().__init__(message, **kwargs)


class SignalScoringError(SignalError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.SIGNAL_SCORING_FAILED)
        super().__init__(message, **kwargs)


class SignalValidationError(SignalError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.SIGNAL_VALIDATION_FAILED)
        super().__init__(message, **kwargs)


class SignalQualityError(SignalError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.SIGNAL_QUALITY_FAILED)
        super().__init__(message, **kwargs)


class SignalCacheError(SignalError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.SIGNAL_CACHE_FAILED)
        super().__init__(message, **kwargs)


class SignalConfluenceError(SignalError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.SIGNAL_CONFLUENCE_FAILED)
        super().__init__(message, **kwargs)


class SignalConflictError(SignalError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.SIGNAL_CONFLICT_FAILED)
        super().__init__(message, **kwargs)


class SignalCalibrationError(SignalError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.SIGNAL_CALIBRATION_FAILED)
        super().__init__(message, **kwargs)


class SignalThresholdError(SignalError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.SIGNAL_THRESHOLD_INVALID)
        super().__init__(message, **kwargs)


class ScoreOutOfRangeError(SignalError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.SCORE_OUT_OF_RANGE)
        super().__init__(message, **kwargs)


class ScoreBreakdownMissingError(SignalError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.SCORE_BREAKDOWN_MISSING)
        super().__init__(message, **kwargs)


class ExecutionThresholdForbiddenError(SignalError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        kwargs.setdefault("error_code", error_codes.EXECUTION_THRESHOLD_FORBIDDEN)
        super().__init__(message, **kwargs)


# Phase 15 Regime Exceptions


class RegimeError(Binance50Error):
    pass


class RegimeConfigError(RegimeError):
    pass


class RegimeFeatureError(RegimeError):
    pass


class RegimeClassificationError(RegimeError):
    pass


class RegimeValidationError(RegimeError):
    pass


class RegimeQualityError(RegimeError):
    pass


class RegimeCacheError(RegimeError):
    pass


class RegimeTransitionError(RegimeError):
    pass


class RegimeStabilityError(RegimeError):
    pass


class RegimeModelAdapterError(RegimeError):
    pass


class RegimeLeakageError(RegimeError):
    pass


class RegimeSmoothingError(RegimeError):
    pass
