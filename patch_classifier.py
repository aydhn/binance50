with open('binance50/src/binance50/core/error_classifier.py', 'r') as f:
    content = f.read()

storage_classifier = """
def classify_storage_error(error: Exception) -> type[Binance50Error]:
    \"\"\"Classify storage related errors.\"\"\"
    from binance50.core.exceptions import (
        StorageError, SQLiteCatalogError, ParquetWriteError,
        ParquetReadError, StoragePathError, StorageSchemaError,
        StorageIntegrityError, DestructiveActionBlockedError
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
"""

with open('binance50/src/binance50/core/error_classifier.py', 'w') as f:
    f.write(content + "\n" + storage_classifier)
