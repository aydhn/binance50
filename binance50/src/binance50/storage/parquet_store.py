import hashlib
import uuid
from pathlib import Path
from typing import Literal

import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.parquet as pq

from binance50.config.models import AppConfig
from binance50.core.exceptions import (
    DestructiveActionBlockedError,
    ParquetReadError,
    ParquetWriteError,
    StorageSchemaError,
)
from binance50.storage.partitions import group_dataframe_by_partitions, partition_filter_to_pyarrow
from binance50.storage.schemas import DatasetSchema, schema_to_pyarrow, validate_dataframe_schema


class ParquetDatasetStore:
    def __init__(self, config: AppConfig):
        self.config = config

    def write_dataset(
        self,
        df: pd.DataFrame,
        dataset_name: str,
        schema: DatasetSchema,
        mode: Literal["append", "overwrite", "upsert"] = "append",
        partition_values: dict | None = None
    ) -> list[Path]:

        if df.empty:
            if self.config.storage.integrity.reject_empty_dataset:
                raise ParquetWriteError("Cannot write empty dataset")
            return []

        if self.config.storage.parquet.schema_validation:
            validate_dataframe_schema(df, schema)

        if mode == "overwrite" and not self.config.storage.parquet.allow_overwrite:
            raise DestructiveActionBlockedError("Overwrite mode is blocked by parquet config allow_overwrite=false")

        if mode == "append" and not self.config.storage.parquet.allow_append:
             raise ParquetWriteError("Append mode is disabled in config")

        if mode == "upsert" and not self.config.storage.parquet.allow_upsert:
             raise ParquetWriteError("Upsert mode is disabled in config")

        groups = group_dataframe_by_partitions(df, self.config, dataset_name)
        pa_schema = schema_to_pyarrow(schema)
        written_files = []

        for spec, group_df in groups.items():
            spec.path.mkdir(parents=True, exist_ok=True)

            # Very basic upsert simulation: if upsert, read existing, concat, drop duplicates, write back
            if mode == "upsert":
                 existing_files = list(spec.path.glob("*.parquet"))
                 if existing_files:
                     try:
                         existing_pa = ds.dataset(spec.path, format="parquet").to_table()
                         existing_df = existing_pa.to_pandas()
                         combined = pd.concat([existing_df, group_df])
                         group_df = combined.drop_duplicates(subset=schema.primary_keys, keep="last")
                     except Exception as e:
                         raise ParquetReadError(f"Failed to read existing data for upsert: {e}")

            file_id = uuid.uuid4().hex
            final_path = spec.path / f"part-{file_id}.parquet"
            temp_path = spec.path / f"part-{file_id}.parquet{self.config.storage.parquet.temp_write_suffix}"

            write_path = temp_path if self.config.storage.parquet.atomic_write else final_path

            try:
                table = pa.Table.from_pandas(group_df, schema=pa_schema, preserve_index=False)
                pq.write_table(
                    table,
                    write_path,
                    compression=self.config.storage.parquet.compression,
                    use_dictionary=self.config.storage.parquet.use_dictionary,
                    row_group_size=self.config.storage.parquet.row_group_size
                )

                if self.config.storage.parquet.atomic_write:
                    write_path.rename(final_path)

                written_files.append(final_path)
            except Exception as e:
                if write_path.exists():
                    write_path.unlink()
                raise ParquetWriteError(f"Failed to write parquet file: {e}")

        if self.config.storage.integrity.verify_after_write:
            self.validate_written_files(written_files, schema)

        return written_files

    def read_dataset(self, dataset_name: str, filters: dict | None = None) -> pd.DataFrame:
        from binance50.storage.paths import get_parquet_root

        # Determine the base path. Note: this is simple and assumes dataset=name at root
        # A robust version would query catalog to find exact files.
        root = get_parquet_root(self.config)
        dataset_path = root / f"dataset={dataset_name}" if self.config.storage.parquet.partition_style == "hive" else root / dataset_name

        if not dataset_path.exists():
             return pd.DataFrame()

        try:
            pa_filters = partition_filter_to_pyarrow(filters) if filters else None
            dataset = ds.dataset(dataset_path, format="parquet", partitioning="hive" if self.config.storage.parquet.partition_style == "hive" else None)

            # Note: PyArrow filtering syntax requires a specific structure, simple DNF list provided earlier might need adjustment
            # For simplicity in this mock-like structure, we fetch all and filter in Pandas if needed,
            # OR assume pa_filters format is correct if used.
            table = dataset.to_table(filter=pa_filters) if pa_filters else dataset.to_table()
            return table.to_pandas()
        except Exception as e:
            raise ParquetReadError(f"Failed to read parquet dataset {dataset_name}: {e}")

    def list_dataset_files(self, dataset_name: str) -> list[Path]:
        from binance50.storage.paths import get_parquet_root
        root = get_parquet_root(self.config)
        # Search all subdirectories
        return list(root.rglob(f"*dataset={dataset_name}*/**/*.parquet")) + list(root.rglob(f"*{dataset_name}*/**/*.parquet"))

    def delete_dataset_files(self, dataset_name: str, dry_run: bool = True) -> list[Path]:
        if not self.config.storage.safety.allow_delete:
             raise DestructiveActionBlockedError("allow_delete is false, physical deletion is blocked")

        files = self.list_dataset_files(dataset_name)
        if not dry_run:
             for f in files:
                 f.unlink()
        return files

    def compact_dataset(self, dataset_name: str, filters: dict | None = None) -> dict:
        # Placeholder for compaction logic
        return {"status": "not_implemented"}

    def validate_written_files(self, paths: list[Path], schema: DatasetSchema) -> None:
        schema_to_pyarrow(schema)
        for p in paths:
             try:
                 pq.read_schema(p)
                 # A real implementation might check columns against pa_schema
             except Exception as e:
                 raise StorageSchemaError(f"Written file {p} failed schema validation: {e}")

    def compute_file_hash(self, path: Path) -> str:
        hasher = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
