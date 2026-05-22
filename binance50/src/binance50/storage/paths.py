import re
from pathlib import Path
from binance50.config.models import AppConfig
from binance50.core.exceptions import StoragePathError

def sanitize_path_component(value: str) -> str:
    """Sanitize a string to be used as a safe directory/file name component."""
    if not value:
        raise StoragePathError("Path component cannot be empty")

    # Block secret-like keywords completely
    lower_val = value.lower()
    if any(secret_word in lower_val for secret_word in ["api_key", "secret", "token", "signature", "password"]):
        raise StoragePathError(f"Secret-like path component blocked: {value}")

    safe_value = re.sub(r'[^a-zA-Z0-9_-]', '_', value)
    if value.startswith('.'):
         raise StoragePathError(f"Invalid path component: {value}")
    if not safe_value:
         raise StoragePathError(f"Invalid path component: {value}")
    return safe_value

def get_storage_root(config: AppConfig) -> Path:
    return Path(config.storage.root_dir).resolve()

def assert_path_inside_storage(path: Path, config: AppConfig) -> None:
    if not config.storage.safety.block_paths_outside_project:
        return

    storage_root = get_storage_root(config)
    resolved_path = path.resolve()

    try:
        resolved_path.relative_to(storage_root)
    except ValueError:
        raise StoragePathError(f"Path traversal detected. {path} is outside {storage_root}")

def get_parquet_root(config: AppConfig) -> Path:
    p = Path(config.storage.parquet_root_dir).resolve()
    assert_path_inside_storage(p, config)
    return p

def get_sqlite_catalog_path(config: AppConfig) -> Path:
    p = Path(config.storage.sqlite_catalog_path).resolve()
    assert_path_inside_storage(p, config)
    return p

def get_manifest_dir(config: AppConfig) -> Path:
    p = Path(config.storage.manifest_dir).resolve()
    assert_path_inside_storage(p, config)
    return p

def get_reports_dir(config: AppConfig) -> Path:
    p = Path(config.storage.reports_dir).resolve()
    assert_path_inside_storage(p, config)
    return p

def get_backups_dir(config: AppConfig) -> Path:
    p = Path(config.storage.backups_dir).resolve()
    assert_path_inside_storage(p, config)
    return p

def get_temp_dir(config: AppConfig) -> Path:
    p = Path(config.storage.temp_dir).resolve()
    assert_path_inside_storage(p, config)
    return p

def get_lock_dir(config: AppConfig) -> Path:
    p = Path(config.storage.lock_dir).resolve()
    assert_path_inside_storage(p, config)
    return p

def ensure_storage_directories(config: AppConfig) -> None:
    """Create all necessary storage directories if they do not exist."""
    dirs = [
        get_storage_root(config),
        get_parquet_root(config),
        get_sqlite_catalog_path(config).parent,
        get_manifest_dir(config),
        get_reports_dir(config),
        get_backups_dir(config),
        get_temp_dir(config),
        get_lock_dir(config)
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

def build_dataset_partition_path(
    config: AppConfig,
    dataset_name: str,
    market_scope: str | None = None,
    symbol: str | None = None,
    interval: str | None = None,
    year: str | int | None = None,
    month: str | int | None = None,
    day: str | int | None = None
) -> Path:

    parts = []

    ds_name = sanitize_path_component(dataset_name)
    parts.append(f"dataset={ds_name}" if config.storage.parquet.partition_style == "hive" else ds_name)

    if market_scope and config.storage.partitioning.by_market_scope:
        parts.append(f"market_scope={sanitize_path_component(market_scope)}" if config.storage.parquet.partition_style == "hive" else sanitize_path_component(market_scope))

    if symbol and config.storage.partitioning.by_symbol:
        parts.append(f"symbol={sanitize_path_component(symbol)}" if config.storage.parquet.partition_style == "hive" else sanitize_path_component(symbol))

    if interval and config.storage.partitioning.by_interval:
        parts.append(f"interval={sanitize_path_component(interval)}" if config.storage.parquet.partition_style == "hive" else sanitize_path_component(interval))

    if year and config.storage.partitioning.by_year:
        parts.append(f"year={sanitize_path_component(str(year))}" if config.storage.parquet.partition_style == "hive" else sanitize_path_component(str(year)))

    if month and config.storage.partitioning.by_month:
        parts.append(f"month={sanitize_path_component(str(month).zfill(2))}" if config.storage.parquet.partition_style == "hive" else sanitize_path_component(str(month).zfill(2)))

    if day and config.storage.partitioning.by_day:
        parts.append(f"day={sanitize_path_component(str(day).zfill(2))}" if config.storage.parquet.partition_style == "hive" else sanitize_path_component(str(day).zfill(2)))

    root = get_parquet_root(config)
    path = root.joinpath(*parts)
    assert_path_inside_storage(path, config)
    return path
