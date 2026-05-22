from pathlib import Path

file_path = Path("src/binance50/storage/importers.py")
content = file_path.read_text()

importer_code = """
def import_indicator_result(result: IndicatorRunResult, config: AppConfig) -> DatasetManifest:
    from binance50.storage.sqlite_catalog import SQLiteCatalog
    from binance50.storage.dataset_registry import DatasetRegistry
    from binance50.storage.parquet_store import ParquetDatasetStore
    from binance50.storage.manifest import build_manifest, write_manifest, manifest_to_catalog_records
    from binance50.storage.schemas import DatasetSchema, ColumnSchema, DatasetKind
    import uuid

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
        ColumnSchema("is_warmup", "bool", nullable=False)
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
        timestamp_column="open_time"
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
        "indicator_count": result.metadata.indicator_count
    }
    manifest = build_manifest(ds_name, version_id, paths, df_to_save, schema, quality_status="pass", metadata=metadata)
    write_manifest(manifest, config)
    registry.register_version(ds_name, manifest, "indicator_engine", "pass")

    records = manifest_to_catalog_records(manifest)
    for r in records:
         catalog.add_file_manifest(r)

    registry.activate_version(version_id)

    return manifest
"""

# Patch DatasetKind in schemas.py
schema_file = Path("src/binance50/storage/schemas.py")
schema_content = schema_file.read_text()
if "INDICATORS = \"indicators\"" not in schema_content:
    schema_content = schema_content.replace("    OHLCV = \"ohlcv\"", "    OHLCV = \"ohlcv\"\n    INDICATORS = \"indicators\"")
    schema_file.write_text(schema_content)

if "def import_indicator_result" not in content:
    content = "from binance50.indicators.models import IndicatorRunResult\n" + content + "\n" + importer_code
    file_path.write_text(content)

print("Patched schemas and importers")
