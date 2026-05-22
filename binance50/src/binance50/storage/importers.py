import pandas as pd
from binance50.config.models import AppConfig
from binance50.storage.manifest import DatasetManifest, build_manifest, write_manifest, manifest_to_catalog_records
from binance50.storage.schemas import get_ohlcv_schema, get_universe_selection_schema, get_stream_events_schema, get_quality_reports_schema, DatasetKind
from binance50.storage.parquet_store import ParquetDatasetStore
from binance50.storage.sqlite_catalog import SQLiteCatalog
from binance50.storage.dataset_registry import DatasetRegistry
from binance50.storage.data_index import DataIndex
from binance50.storage.quality_index import QualityIndex
import uuid

def _ensure_dataset(registry: DatasetRegistry, name: str, kind: DatasetKind, schema):
    existing = registry.catalog.get_dataset(name)
    if not existing:
         registry.register_dataset(name, kind, schema)

def import_ohlcv_dataframe(df: pd.DataFrame, symbol: str, market_scope: str, interval: str, source: str, config: AppConfig) -> DatasetManifest:
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
    manifest = build_manifest(ds_name, version_id, paths, df, schema, quality_status="pass", metadata={"source": source})
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

def import_ohlcv_cache(symbol: str, market_scope: str, interval: str, config: AppConfig) -> DatasetManifest:
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
    manifest = build_manifest(ds_name, version_id, paths, df, schema, quality_status="pass", metadata={"source": "fixture"})
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
    manifest = build_manifest(ds_name, version_id, paths, df, schema, quality_status="pass", metadata={"source": "fixture"})
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
    manifest = build_manifest(ds_name, version_id, paths, df, schema, quality_status="pass", metadata={"source": "fixture"})
    write_manifest(manifest, config)
    registry.register_version(ds_name, manifest, "fixture", "pass")
    records = manifest_to_catalog_records(manifest)
    for r in records:
         catalog.add_file_manifest(r)
    registry.activate_version(version_id)

    return manifest
