import re

with open('binance50/config/default.yaml', 'r') as f:
    content = f.read()

storage_config = """
storage:
  enabled: true
  root_dir: data/warehouse
  parquet_root_dir: data/warehouse/parquet
  sqlite_catalog_path: data/warehouse/catalog/binance50_catalog.sqlite
  manifest_dir: data/warehouse/manifests
  reports_dir: data/warehouse/reports
  backups_dir: data/warehouse/backups
  exports_dir: data/warehouse/exports
  temp_dir: data/warehouse/tmp
  lock_dir: data/warehouse/locks
  parquet:
    enabled: true
    compression: zstd
    fallback_compression: snappy
    use_dictionary: true
    write_statistics: true
    row_group_size: 100000
    max_rows_per_file: 500000
    partition_style: hive
    schema_validation: true
    atomic_write: true
    temp_write_suffix: .tmp
    allow_overwrite: false
    allow_append: true
    allow_upsert: true
  sqlite:
    enabled: true
    journal_mode: WAL
    synchronous: NORMAL
    foreign_keys: true
    busy_timeout_ms: 5000
    integrity_check_on_start: true
    quick_check_on_doctor: true
    vacuum_on_compaction: false
    backup_before_migration: true
  partitioning:
    by_market_scope: true
    by_symbol: true
    by_interval: true
    by_year: true
    by_month: true
    by_day: false
  datasets:
    ohlcv_dataset_name: ohlcv
    universe_dataset_name: universe_selection
    stream_events_dataset_name: stream_events
    quality_dataset_name: quality_reports
    allowed_dataset_names:
      - ohlcv
      - universe_selection
      - stream_events
      - quality_reports
      - feature_store_future
      - backtest_results_future
  integrity:
    compute_file_hash: true
    compute_dataframe_hash: true
    verify_after_write: true
    verify_before_read: true
    reject_schema_drift: true
    reject_duplicate_primary_keys: true
    reject_empty_dataset: true
  retention:
    enabled: false
    max_versions_per_dataset: 20
    keep_latest_versions: 5
    archive_old_versions: true
    delete_archived_after_days: 365
  backup:
    enabled: true
    backup_catalog: true
    backup_manifests: true
    backup_parquet_metadata_only: true
    max_backups: 20
  safety:
    allow_delete: false
    allow_destructive_migration: false
    require_backup_before_migration: true
    block_paths_outside_project: true
    block_secret_columns: true
    block_unknown_dataset_names: true
"""

with open('binance50/config/default.yaml', 'w') as f:
    f.write(content + "\n" + storage_config)
