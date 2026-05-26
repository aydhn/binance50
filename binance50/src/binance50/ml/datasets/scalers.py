from typing import Protocol, Any
import pandas as pd

from binance50.config.models import AppConfig
from binance50.core.exceptions import MLScalerError

class MLScalerProtocol(Protocol):
    def fit(self, train_values: pd.DataFrame | pd.Series) -> None:
        ...

    def transform(self, values: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
        ...

    def get_metadata(self) -> dict[str, Any]:
        ...

class NoOpScaler(MLScalerProtocol):
    def fit(self, train_values: pd.DataFrame | pd.Series) -> None:
        pass

    def transform(self, values: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
        return values

    def get_metadata(self) -> dict[str, Any]:
        return {"type": "noop"}

class StandardScalerAdapter(MLScalerProtocol):
    def __init__(self):
        self.means_ = None
        self.stds_ = None
        self._is_fitted = False

    def fit(self, train_values: pd.DataFrame | pd.Series) -> None:
        if isinstance(train_values, pd.DataFrame):
            self.means_ = train_values.mean()
            self.stds_ = train_values.std().replace(0, 1e-10) # Avoid div zero
        else:
             self.means_ = train_values.mean()
             self.stds_ = train_values.std() or 1e-10
        self._is_fitted = True

    def transform(self, values: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
        if not self._is_fitted:
            raise MLScalerError("Scaler not fitted yet.")
        return (values - self.means_) / self.stds_

    def get_metadata(self) -> dict[str, Any]:
        return {"type": "standard"}

class RobustScalerAdapter(MLScalerProtocol):
    def __init__(self):
        self.medians_ = None
        self.iqrs_ = None
        self._is_fitted = False

    def fit(self, train_values: pd.DataFrame | pd.Series) -> None:
        if isinstance(train_values, pd.DataFrame):
             self.medians_ = train_values.median()
             q75 = train_values.quantile(0.75)
             q25 = train_values.quantile(0.25)
             self.iqrs_ = (q75 - q25).replace(0, 1e-10)
        else:
             self.medians_ = train_values.median()
             self.iqrs_ = (train_values.quantile(0.75) - train_values.quantile(0.25)) or 1e-10
        self._is_fitted = True

    def transform(self, values: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
        if not self._is_fitted:
            raise MLScalerError("Scaler not fitted yet.")
        return (values - self.medians_) / self.iqrs_

    def get_metadata(self) -> dict[str, Any]:
        return {"type": "robust"}

class MinMaxScalerAdapter(MLScalerProtocol):
    def __init__(self):
        self.mins_ = None
        self.maxs_ = None
        self._is_fitted = False

    def fit(self, train_values: pd.DataFrame | pd.Series) -> None:
        if isinstance(train_values, pd.DataFrame):
             self.mins_ = train_values.min()
             self.maxs_ = train_values.max()
        else:
             self.mins_ = train_values.min()
             self.maxs_ = train_values.max()
        self._is_fitted = True

    def transform(self, values: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
         if not self._is_fitted:
             raise MLScalerError("Scaler not fitted yet.")
         ranges = (self.maxs_ - self.mins_)
         if isinstance(ranges, pd.Series):
             ranges = ranges.replace(0, 1e-10)
         elif ranges == 0:
             ranges = 1e-10
         return (values - self.mins_) / ranges

    def get_metadata(self) -> dict[str, Any]:
        return {"type": "minmax"}

def build_scaler(config: AppConfig) -> MLScalerProtocol:
    if not config.ml_dataset or not config.ml_dataset.preprocessing.enabled:
         return NoOpScaler()

    scaler_type = config.ml_dataset.preprocessing.scaler.lower()

    if scaler_type == "none":
        return NoOpScaler()
    elif scaler_type == "standard":
        return StandardScalerAdapter()
    elif scaler_type == "robust":
        return RobustScalerAdapter()
    elif scaler_type == "minmax":
        return MinMaxScalerAdapter()
    else:
        raise MLScalerError(f"Unsupported scaler type: {scaler_type}")

def validate_scaler_metadata(metadata: dict[str, Any], config: AppConfig) -> None:
    pass
