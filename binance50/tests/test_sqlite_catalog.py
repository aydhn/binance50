from binance50.config.models import AppConfig
from binance50.storage.catalog_models import DatasetRecord
from binance50.storage.sqlite_catalog import SQLiteCatalog


def test_sqlite_catalog_init(tmp_path):
    config = AppConfig()
    db_path = tmp_path / "test.sqlite"
    cat = SQLiteCatalog(config, path=db_path)

    cat.initialize()

    # Needs tables to actually work, just testing connection here
    conn = cat.connect()
    assert conn is not None
    cat.close()

def test_sqlite_catalog_upsert(tmp_path):
    config = AppConfig()
    db_path = tmp_path / "test.sqlite"
    cat = SQLiteCatalog(config, path=db_path)
    cat.initialize()

    # Create table for test manually since migrations aren't run
    with cat.transaction() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
                dataset_id TEXT PRIMARY KEY,
                dataset_name TEXT UNIQUE NOT NULL,
                dataset_kind TEXT NOT NULL,
                schema_version INTEGER NOT NULL,
                status TEXT NOT NULL,
                created_at_utc TEXT NOT NULL,
                updated_at_utc TEXT NOT NULL,
                description TEXT
            )
        """)

    rec = DatasetRecord("1", "test_ds", "ohlcv", 1, "active", "2024", "2024", "desc")
    cat.upsert_dataset(rec)

    fetched = cat.get_dataset("test_ds")
    assert fetched is not None
    assert fetched.dataset_id == "1"
