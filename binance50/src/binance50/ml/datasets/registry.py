from typing import Any
from binance50.ml.datasets.models import MLDatasetManifest

class MLDatasetRegistry:
    def __init__(self):
        self._manifests: dict[str, MLDatasetManifest] = {}

    def register_dataset(self, manifest: MLDatasetManifest) -> None:
        self._manifests[manifest.dataset_id] = manifest

    def get_dataset(self, dataset_id: str) -> MLDatasetManifest | None:
        return self._manifests.get(dataset_id)

    def list_datasets(self, symbol: str | None = None, interval: str | None = None) -> list[MLDatasetManifest]:
        return list(self._manifests.values())

    def get_latest_dataset(self, symbol: str, market_scope: str, interval: str) -> MLDatasetManifest | None:
        return next(iter(self._manifests.values()), None)

    def deactivate_dataset(self, dataset_id: str) -> None:
        pass

    def validate_registry(self) -> None:
        pass

    def to_report(self) -> dict[str, Any]:
        return {"total_datasets": len(self._manifests)}
