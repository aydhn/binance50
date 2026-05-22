with open('binance50/src/binance50/core/exceptions.py', 'r') as f:
    content = f.read()

storage_exceptions = """
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

"""

with open('binance50/src/binance50/core/exceptions.py', 'w') as f:
    f.write(content + "\n" + storage_exceptions)
