import uuid

import pandas as pd

from binance50.config.models import AppConfig
from binance50.indicators.models import IndicatorRunResult
from binance50.storage.data_index import DataIndex
from binance50.storage.dataset_registry import DatasetRegistry
from binance50.storage.manifest import (
    DatasetManifest,
    build_manifest,
    manifest_to_catalog_records,
    write_manifest,
)
from binance50.storage.parquet_store import ParquetDatasetStore
from binance50.storage.quality_index import QualityIndex
from binance50.storage.schemas import (
    DatasetKind,
    get_ohlcv_schema,
    get_quality_reports_schema,
    get_stream_events_schema,
    get_universe_selection_schema,
)
from binance50.storage.sqlite_catalog import SQLiteCatalog


def _ensure_dataset(registry: DatasetRegistry, name: str, kind: DatasetKind, schema):
    existing = registry.catalog.get_dataset(name)
    if not existing:
        registry.register_dataset(name, kind, schema)


def import_ohlcv_dataframe(
    df: pd.DataFrame, symbol: str, market_scope: str, interval: str, source: str, config: AppConfig
) -> DatasetManifest:
    # Ensure dataset
    catalog = SQLiteCatalog(config)
    registry = DatasetRegistry(config, catalog)
    schema = get_ohlcv_schema()
    ds_name = config.storage.datasets.ohlcv_dataset_name
    _ensure_dataset(registry, ds_name, DatasetKind.OHLCV, schema)

    # Write parquet
    store = ParquetDatasetStore(config)
    paths = store.write_dataset(df, ds_name, schema, mode="append")

    # Build manifest
    version_id = uuid.uuid4().hex
    manifest = build_manifest(
        ds_name, version_id, paths, df, schema, quality_status="pass", metadata={"source": source}
    )
    write_manifest(manifest, config)

    # Register version
    registry.register_version(ds_name, manifest, source, "pass")

    # Add files to catalog
    records = manifest_to_catalog_records(manifest)
    for r in records:
        catalog.add_file_manifest(r)

    # Update Data Index
    di = DataIndex(catalog)
    coverage = di.build_coverage_from_ohlcv(df, version_id)
    di.upsert_coverage(coverage)

    # Activate
    registry.activate_version(version_id)

    return manifest


def import_ohlcv_cache(
    symbol: str, market_scope: str, interval: str, config: AppConfig
) -> DatasetManifest:
    # Logic to load from old cache and route to new via dataframe
    # This acts as a bridge. For actual data fetching see old cache
    pass


def import_universe_selection(result: dict, config: AppConfig) -> DatasetManifest:
    catalog = SQLiteCatalog(config)
    registry = DatasetRegistry(config, catalog)
    schema = get_universe_selection_schema()
    ds_name = config.storage.datasets.universe_dataset_name
    _ensure_dataset(registry, ds_name, DatasetKind.UNIVERSE_SELECTION, schema)

    df = pd.DataFrame(result.get("selections", []))
    if df.empty:
        from binance50.core.exceptions import DataValidationError

        raise DataValidationError("Empty universe selection result")

    store = ParquetDatasetStore(config)
    paths = store.write_dataset(df, ds_name, schema, mode="append")

    version_id = uuid.uuid4().hex
    manifest = build_manifest(
        ds_name,
        version_id,
        paths,
        df,
        schema,
        quality_status="pass",
        metadata={"source": "fixture"},
    )
    write_manifest(manifest, config)
    registry.register_version(ds_name, manifest, "fixture", "pass")
    records = manifest_to_catalog_records(manifest)
    for r in records:
        catalog.add_file_manifest(r)
    registry.activate_version(version_id)

    return manifest


def import_stream_events(events: list, config: AppConfig) -> DatasetManifest:
    catalog = SQLiteCatalog(config)
    registry = DatasetRegistry(config, catalog)
    schema = get_stream_events_schema()
    ds_name = config.storage.datasets.stream_events_dataset_name
    _ensure_dataset(registry, ds_name, DatasetKind.STREAM_EVENTS, schema)

    df = pd.DataFrame(events)
    store = ParquetDatasetStore(config)
    paths = store.write_dataset(df, ds_name, schema, mode="append")

    version_id = uuid.uuid4().hex
    manifest = build_manifest(
        ds_name,
        version_id,
        paths,
        df,
        schema,
        quality_status="pass",
        metadata={"source": "fixture"},
    )
    write_manifest(manifest, config)
    registry.register_version(ds_name, manifest, "fixture", "pass")
    records = manifest_to_catalog_records(manifest)
    for r in records:
        catalog.add_file_manifest(r)
    registry.activate_version(version_id)

    return manifest


def import_quality_report(report: dict, config: AppConfig) -> DatasetManifest:
    # First, import it into the Quality Index (SQLite)
    catalog = SQLiteCatalog(config)
    qi = QualityIndex(catalog)
    # Using a fake version_id for report import directly
    qi.index_quality_report("report_import", "ohlcv", report)

    # Second, write it as a dataset
    registry = DatasetRegistry(config, catalog)
    schema = get_quality_reports_schema()
    ds_name = config.storage.datasets.quality_dataset_name
    _ensure_dataset(registry, ds_name, DatasetKind.QUALITY_REPORTS, schema)

    df = pd.DataFrame([report])
    store = ParquetDatasetStore(config)
    paths = store.write_dataset(df, ds_name, schema, mode="append")

    version_id = uuid.uuid4().hex
    manifest = build_manifest(
        ds_name,
        version_id,
        paths,
        df,
        schema,
        quality_status="pass",
        metadata={"source": "fixture"},
    )
    write_manifest(manifest, config)
    registry.register_version(ds_name, manifest, "fixture", "pass")
    records = manifest_to_catalog_records(manifest)
    for r in records:
        catalog.add_file_manifest(r)
    registry.activate_version(version_id)

    return manifest


def import_indicator_result(result: IndicatorRunResult, config: AppConfig) -> DatasetManifest:
    import uuid

    from binance50.storage.dataset_registry import DatasetRegistry
    from binance50.storage.manifest import (
        build_manifest,
        manifest_to_catalog_records,
        write_manifest,
    )
    from binance50.storage.parquet_store import ParquetDatasetStore
    from binance50.storage.schemas import ColumnSchema, DatasetKind, DatasetSchema
    from binance50.storage.sqlite_catalog import SQLiteCatalog

    if not result.success or result.output_df is None:
        raise ValueError("Cannot import failed indicator result")

    catalog = SQLiteCatalog(config)
    registry = DatasetRegistry(config, catalog)

    ds_name = config.indicators.output_dataset_name

    # We must build a dynamic schema for indicators based on the output columns
    base_cols = [
        ColumnSchema("market_scope", "string", nullable=False, is_primary_key=True),
        ColumnSchema("symbol", "string", nullable=False, is_primary_key=True),
        ColumnSchema("interval", "string", nullable=False, is_primary_key=True),
        ColumnSchema("open_time", "int64", nullable=False, is_primary_key=True),
        ColumnSchema("close_time", "int64", nullable=False),
        ColumnSchema("config_hash", "string", nullable=False, is_primary_key=True),
        ColumnSchema("is_warmup", "bool", nullable=False),
    ]

    # Exclude base columns from dynamic discovery
    base_col_names = {c.name for c in base_cols}
    dynamic_cols = []

    for col in result.output_df.columns:
        if col not in base_col_names:
            dynamic_cols.append(ColumnSchema(col, "float64", nullable=True))

    schema = DatasetSchema(
        dataset_name=ds_name,
        dataset_kind=DatasetKind.INDICATORS,
        version=1,
        columns=base_cols + dynamic_cols,
        primary_keys=["market_scope", "symbol", "interval", "open_time", "config_hash"],
        partition_columns=["market_scope", "symbol", "interval"],
        timestamp_column="open_time",
    )

    from binance50.storage.importers import _ensure_dataset

    _ensure_dataset(registry, ds_name, DatasetKind.INDICATORS, schema)

    store = ParquetDatasetStore(config)

    # Add necessary primary key columns to DF before saving
    df_to_save = result.output_df.copy()
    df_to_save["market_scope"] = result.request.market_scope.value
    df_to_save["symbol"] = result.request.symbol
    df_to_save["interval"] = result.request.interval
    df_to_save["config_hash"] = result.metadata.config_hash

    paths = store.write_dataset(df_to_save, ds_name, schema, mode="append")

    version_id = uuid.uuid4().hex
    metadata = {
        "source": "indicator_engine",
        "backend": result.request.backend,
        "indicator_count": result.metadata.indicator_count,
    }
    manifest = build_manifest(
        ds_name, version_id, paths, df_to_save, schema, quality_status="pass", metadata=metadata
    )
    write_manifest(manifest, config)
    registry.register_version(ds_name, manifest, "indicator_engine", "pass")

    records = manifest_to_catalog_records(manifest)
    for r in records:
        catalog.add_file_manifest(r)

    registry.activate_version(version_id)

    return manifest


def import_indicator_v2_result(result, config: AppConfig) -> DatasetManifest:
    import uuid

    from binance50.core.exceptions import FeatureQualityError
    from binance50.storage.dataset_registry import DatasetRegistry
    from binance50.storage.manifest import (
        build_manifest,
        manifest_to_catalog_records,
        write_manifest,
    )
    from binance50.storage.parquet_store import ParquetDatasetStore
    from binance50.storage.schemas import INDICATOR_V2_SCHEMA, DatasetKind
    from binance50.storage.sqlite_catalog import SQLiteCatalog

    if not result.success or result.output_df is None:
        raise ValueError("Cannot import failed indicator v2 result")

    if result.quality_report and result.quality_report.status == "fail":
        raise FeatureQualityError("Cannot import indicator v2 result that failed quality checks")

    catalog = SQLiteCatalog(config)
    registry = DatasetRegistry(config, catalog)

    ds_name = config.indicator_v2.output_dataset_name

    schema = INDICATOR_V2_SCHEMA
    _ensure_dataset(registry, ds_name, DatasetKind.INDICATOR_FEATURES_V2, schema)

    df = result.output_df

    store = ParquetDatasetStore(config)
    paths = store.write_dataset(df, ds_name, schema, mode="append")

    version_id = uuid.uuid4().hex

    metadata = {
        "source": "indicator_engine_v2",
        "request_id": result.request.request_id if result.request else None,
    }

    if result.feature_set_metadata:
        # Avoid direct object serialization issues
        metadata["feature_set_id"] = result.feature_set_metadata.feature_set_id
        metadata["feature_count"] = result.feature_set_metadata.feature_count
        metadata["config_hash"] = result.feature_set_metadata.config_hash

    manifest = build_manifest(
        ds_name, version_id, paths, df, schema, quality_status="pass", metadata=metadata
    )
    write_manifest(manifest, config)

    registry.register_version(ds_name, manifest, "indicator_engine_v2", "pass")

    records = manifest_to_catalog_records(manifest)
    for r in records:
        catalog.add_file_manifest(r)

    # Automatically activate if quality checks passed (checked above)
    registry.activate_version(version_id)

    return manifest


def import_strategy_result(result, config: AppConfig):
    import uuid

    from binance50.core.exceptions import StrategyQualityError
    from binance50.storage.dataset_registry import DatasetRegistry
    from binance50.storage.manifest import (
        build_manifest,
        manifest_to_catalog_records,
        write_manifest,
    )
    from binance50.storage.parquet_store import ParquetDatasetStore
    from binance50.storage.schemas import DatasetKind, get_strategy_candidates_schema
    from binance50.storage.sqlite_catalog import SQLiteCatalog

    if not result.success:
        raise ValueError("Cannot import failed strategy result")

    if result.quality_report and result.quality_report.status == "fail":
        raise StrategyQualityError("Cannot import strategy result that failed quality checks")

    # Extra runtime safety assertion
    from binance50.safety.strategy_guard import assert_no_execution_objects

    for c in result.candidates:
        assert_no_execution_objects(c)

    catalog = SQLiteCatalog(config)
    registry = DatasetRegistry(config, catalog)
    schema = get_strategy_candidates_schema()
    ds_name = config.strategies.output_dataset_name

    from binance50.storage.importers import _ensure_dataset

    _ensure_dataset(registry, ds_name, DatasetKind.STRATEGY_CANDIDATES, schema)

    from binance50.strategies.candidates import candidates_to_dataframe

    df = candidates_to_dataframe(result.candidates)

    if df.empty:
        # Optionally allow importing empty frames if acceptable
        return None

    store = ParquetDatasetStore(config)

    # Needs config_hash in dataframe for schema compliance
    df["config_hash"] = result.metadata.config_hash

    paths = store.write_dataset(df, ds_name, schema, mode="append")

    version_id = uuid.uuid4().hex
    metadata = {
        "source": "strategy_engine",
        "request_id": result.request.request_id,
        "config_hash": result.metadata.config_hash,
        "candidates_count": len(result.candidates),
        "explanation_metadata": [
            c.explanation.summary for c in result.candidates[:5]
        ],  # Keep partial
    }

    manifest = build_manifest(
        ds_name, version_id, paths, df, schema, quality_status="pass", metadata=metadata
    )
    write_manifest(manifest, config)
    registry.register_version(ds_name, manifest, "strategy_engine", "pass")

    records = manifest_to_catalog_records(manifest)
    for r in records:
        catalog.add_file_manifest(r)

    registry.activate_version(version_id)
    return manifest
