# Phase 10: Local Data Warehouse

I've successfully implemented the Phase 10 hybrid local data warehouse for the binance50 project.

## Created/Updated Files
- `config/default.yaml` and `src/binance50/config/models.py`: Added comprehensive storage configuration with Parquet and SQLite options, integrity rules, paths, retention, backup, and safety guards.
- `src/binance50/core/exceptions.py`, `error_codes.py`, `error_classifier.py`: Added detailed error classes and classifiers for all storage scenarios.
- `src/binance50/storage/*`: Implemented the full suite of storage modules, including Parquet stores, SQLite catalog models, schema registry, dataset and snapshot registries, manifest generators, data and quality indexes, health checks, backups, compaction, retention planners, and report generators.
- `src/binance50/safety/storage_guard.py`: Added a rigorous guard ensuring local paths, schema configurations, and operations don't violate safety guidelines (blocking secret fields, destructive commands, or path traversals).
- `src/binance50/market_data/store.py`, `src/binance50/universe/cache.py`, `src/binance50/streams/replay.py`: Hooked into the new importer functions so older fixture flows directly push to the warehouse.
- `src/binance50/cli.py`: Integrated extensive storage CLI endpoints (e.g. `storage-init`, `storage-import-ohlcv-fixture`, `storage-dataset-summary`, `storage-integrity-check`, etc.).

## Storage Config Decisions
The system defaults to a safe, read/append-only operational mode. Parquet files are written atomically (`.tmp` suffixes) with zstd compression using a Hive-style partition scheme. Overwrites, physical deletions, and destructive schema migrations are strictly blocked via the `StorageSafetyConfig`.

## Parquet Store Architecture
Massive datasets (like OHLCV) are mapped via `DatasetSchema` definitions enforcing strict typing. Files are written dynamically into partition paths (e.g. `dataset=ohlcv/market_scope=spot/...`) avoiding complex full-table locks during appends. Upserts are performed safely via appending deduplicated chunks back to storage.

## SQLite Catalog Architecture
SQLite (running in WAL mode) stores operational metadata preventing the need for heavy folder walks. Models are stored across tables like `datasets`, `dataset_versions`, `file_manifests`, `quality_index`, and `data_index`. A sequential migration tool was created strictly for SQLite schema rollouts.

## Indexing, Manifest, and Partition Management
When data is written to Parquet, a lightweight `DatasetManifest` is produced and mapped directly to SQLite. This tracks file hashes, timestamps, and row counts allowing operations like increment fetching to calculate overlaps purely from metadata. The `QualityIndex` and `DataIndex` extract coverage and gap summaries directly into SQLite for query optimization before launching into heavy ML or Backtesting runs later.

## Test Results
New `test_storage_*.py` files confirm the schemas map correctly, path boundaries are secure, configurations align, and SQLite migrations properly trigger backups. Existing tests verify the entire suite remains stable. The integrity checks (`python scripts/check_project.py`) correctly parse the imported fixtures.

## Phase 11 Preparation
With historical OHLCV data reliably partitioned and accessible through the new warehouse, the system is fully decoupled from live streams, creating a deterministic foundation. Phase 11 will ingest this clean, gap-validated Parquet data to calculate trends, momentum, volatility, and volume indicators.
