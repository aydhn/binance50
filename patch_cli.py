import re

with open('binance50/src/binance50/cli.py', 'r') as f:
    content = f.read()

cli_methods = """
@app.command()
def storage_config() -> None:
    \"\"\"Display storage configuration summary.\"\"\"
    config = get_config()
    from binance50.storage.reports import build_storage_config_report
    rep = build_storage_config_report(config)
    console.print(rep)

@app.command()
def storage_init() -> None:
    \"\"\"Initialize storage directories and catalog.\"\"\"
    config = get_config()
    from binance50.storage.paths import ensure_storage_directories
    from binance50.storage.sqlite_catalog import SQLiteCatalog
    from binance50.storage.migrations import StorageMigrationManager

    ensure_storage_directories(config)
    cat = SQLiteCatalog(config)
    cat.initialize()
    mgr = StorageMigrationManager(config, cat)
    mgr.apply_migrations()
    cat.run_quick_check()
    console.print("[green]Storage initialized successfully.[/green]")

@app.command()
def storage_health() -> None:
    \"\"\"Run storage health checks.\"\"\"
    config = get_config()
    from binance50.storage.reports import build_storage_health_report
    rep = build_storage_health_report(config)
    console.print(rep)

@app.command()
def storage_integrity_check() -> None:
    \"\"\"Run storage integrity check.\"\"\"
    config = get_config()
    from binance50.storage.sqlite_catalog import SQLiteCatalog
    from binance50.storage.parquet_store import ParquetDatasetStore
    from binance50.storage.integrity import StorageIntegrityChecker, StorageIntegrityReport
    from binance50.storage.reports import build_integrity_report_view

    cat = SQLiteCatalog(config)
    store = ParquetDatasetStore(config)
    checker = StorageIntegrityChecker(config, cat, store)

    report = checker.run_full_check()
    view = build_integrity_report_view(report)
    console.print(view)
    if report.status == "error":
        raise typer.Exit(1)

@app.command()
def storage_list_datasets() -> None:
    \"\"\"List datasets registered in catalog.\"\"\"
    config = get_config()
    from binance50.storage.sqlite_catalog import SQLiteCatalog
    from binance50.storage.reports import format_dataset_table
    cat = SQLiteCatalog(config)
    records = cat.list_datasets()
    console.print(format_dataset_table(records))

@app.command()
def storage_list_versions(dataset: str = typer.Option(..., "--dataset", help="Dataset name")) -> None:
    \"\"\"List versions of a dataset.\"\"\"
    config = get_config()
    from binance50.storage.sqlite_catalog import SQLiteCatalog
    from binance50.storage.reports import format_versions_table
    cat = SQLiteCatalog(config)
    records = cat.list_versions(dataset)
    console.print(format_versions_table(records))

@app.command()
def storage_list_files(dataset: str = typer.Option(..., "--dataset", help="Dataset name")) -> None:
    \"\"\"List files for active version of dataset.\"\"\"
    config = get_config()
    from binance50.storage.sqlite_catalog import SQLiteCatalog
    from binance50.storage.reports import format_files_table
    cat = SQLiteCatalog(config)
    v = cat.get_latest_active_version(dataset)
    if not v:
        console.print(f"[yellow]No active version found for {dataset}[/yellow]")
        return
    records = cat.list_files(v.version_id)
    console.print(format_files_table(records))

@app.command()
def storage_import_ohlcv_fixture(
    fixture: str = typer.Option(..., help="Fixture filename"),
    symbol: str = typer.Option(..., help="Symbol"),
    scope: str = typer.Option(..., help="Market Scope"),
    interval: str = typer.Option(..., help="Interval")
) -> None:
    \"\"\"Import OHLCV fixture to storage.\"\"\"
    config = get_config()
    from binance50.market_data.store import OHLCVStore
    from binance50.core.models import MarketScope

    store = OHLCVStore(config)
    # Re-use existing cache load which loads fixtures in our mock setup
    try:
         df = store.load_from_cache(symbol, MarketScope(scope), interval)
         if df is not None and not df.empty:
              from binance50.storage.importers import import_ohlcv_dataframe
              import_ohlcv_dataframe(df, symbol, scope, interval, "fixture", config)
              console.print("[green]Imported successfully.[/green]")
         else:
              console.print("[red]Failed to load fixture.[/red]")
    except Exception as e:
         console.print(f"[red]Import failed: {e}[/red]")
         raise typer.Exit(1)

@app.command()
def storage_import_universe_fixture() -> None:
    \"\"\"Import universe selection fixture to storage.\"\"\"
    config = get_config()
    # Mocking for Phase 10
    from binance50.storage.importers import import_universe_selection
    try:
         import_universe_selection({"selections": [{"selection_id":"mock", "symbol":"BTCUSDT", "status":"passed", "market_scope":"spot", "generated_at_ms":0, "base_asset":"BTC", "quote_asset":"USDT"}]}, config)
         console.print("[green]Imported successfully.[/green]")
    except Exception as e:
         console.print(f"[red]Import failed: {e}[/red]")
         raise typer.Exit(1)

@app.command()
def storage_import_stream_fixtures() -> None:
    \"\"\"Import stream events fixture to storage.\"\"\"
    config = get_config()
    from binance50.storage.importers import import_stream_events
    try:
         import_stream_events([{"event_id":"e1", "stream_type":"kline", "symbol":"BTCUSDT", "event_time_ms":0, "payload":"{}"}], config)
         console.print("[green]Imported successfully.[/green]")
    except Exception as e:
         console.print(f"[red]Import failed: {e}[/red]")
         raise typer.Exit(1)

@app.command()
def storage_dataset_summary(dataset: str = typer.Option(..., "--dataset", help="Dataset name")) -> None:
    \"\"\"Show summary for dataset.\"\"\"
    config = get_config()
    from binance50.storage.sqlite_catalog import SQLiteCatalog
    from binance50.storage.reports import build_dataset_summary
    cat = SQLiteCatalog(config)
    rep = build_dataset_summary(dataset, cat)
    console.print(rep)

@app.command()
def storage_quality_summary(dataset: str = typer.Option(..., "--dataset", help="Dataset name")) -> None:
    \"\"\"Show quality summary for dataset.\"\"\"
    config = get_config()
    from binance50.storage.sqlite_catalog import SQLiteCatalog
    from binance50.storage.quality_index import QualityIndex
    cat = SQLiteCatalog(config)
    qi = QualityIndex(cat)
    rep = qi.summarize_quality(dataset)
    console.print(rep)

@app.command()
def storage_coverage(dataset: str = typer.Option(..., "--dataset", help="Dataset name")) -> None:
    \"\"\"Show data coverage for dataset.\"\"\"
    config = get_config()
    from binance50.storage.sqlite_catalog import SQLiteCatalog
    from binance50.storage.data_index import DataIndex
    cat = SQLiteCatalog(config)
    di = DataIndex(cat)
    cov = di.list_coverage(dataset)
    console.print([c.__dict__ for c in cov])

@app.command()
def storage_export_catalog() -> None:
    \"\"\"Export catalog to JSON.\"\"\"
    config = get_config()
    from binance50.storage.export import export_catalog_to_json
    path = export_catalog_to_json(config)
    console.print(f"[green]Exported to {path}[/green]")

@app.command()
def storage_backup_catalog() -> None:
    \"\"\"Backup catalog to backup dir.\"\"\"
    config = get_config()
    from binance50.storage.backup import StorageBackupManager
    mgr = StorageBackupManager(config)
    path = mgr.backup_catalog("cli_manual_backup")
    console.print(f"[green]Backed up to {path}[/green]")

@app.command()
def storage_compaction_plan(dataset: str = typer.Option(..., "--dataset", help="Dataset name")) -> None:
    \"\"\"Show compaction plan for dataset.\"\"\"
    config = get_config()
    from binance50.storage.sqlite_catalog import SQLiteCatalog
    from binance50.storage.parquet_store import ParquetDatasetStore
    from binance50.storage.compaction import StorageCompactor

    cat = SQLiteCatalog(config)
    store = ParquetDatasetStore(config)
    compactor = StorageCompactor(config, cat, store)

    plan = compactor.plan_compaction(dataset)
    console.print(plan.__dict__)

@app.command()
def storage_retention_plan(dataset: str = typer.Option(..., "--dataset", help="Dataset name")) -> None:
    \"\"\"Show retention plan for dataset.\"\"\"
    config = get_config()
    from binance50.storage.sqlite_catalog import SQLiteCatalog
    from binance50.storage.retention import StorageRetentionManager
    cat = SQLiteCatalog(config)
    mgr = StorageRetentionManager(config, cat)
    plan = mgr.plan_retention(dataset)
    console.print(plan.__dict__)

@app.command()
def storage_safety_check() -> None:
    \"\"\"Run storage safety guard checks.\"\"\"
    config = get_config()
    from binance50.safety.storage_guard import build_storage_safety_report, assert_storage_config_safe
    assert_storage_config_safe(config)
    rep = build_storage_safety_report(config)
    console.print(rep)

"""

# Insert commands into cli.py
content = content.replace(
    "@app.command()\ndef show_config() -> None:",
    cli_methods + "\n@app.command()\ndef show_config() -> None:"
)

with open('binance50/src/binance50/cli.py', 'w') as f:
    f.write(content)
