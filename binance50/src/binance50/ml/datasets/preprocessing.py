import pandas as pd
from datetime import datetime

from binance50.config.models import AppConfig
from binance50.core.exceptions import MLPreprocessingError
from binance50.ml.datasets.models import MLPreprocessorMetadata, MLSplitName
from binance50.ml.datasets.scalers import build_scaler, MLScalerProtocol


class MLPreprocessingPipeline:
    def __init__(self, config: AppConfig):
        self.config = config
        self.scaler: MLScalerProtocol = build_scaler(config)
        self.feature_columns: list[str] = []
        self._is_fitted = False

    def fit_train(self, train_df: pd.DataFrame, feature_columns: list[str]) -> MLPreprocessorMetadata:
        if not self.config.ml_dataset or not self.config.ml_dataset.preprocessing.enabled:
             self._is_fitted = True
             return self.export_metadata()

        if not self.config.ml_dataset.preprocessing.fit_transform_train_only:
             raise MLPreprocessingError("Global fit is forbidden. Scaler must only be fit on train data.")

        if self.config.ml_dataset.preprocessing.imputation.allow_bfill:
             raise MLPreprocessingError("bfill is forbidden to prevent lookahead bias.")

        self.feature_columns = feature_columns

        if not train_df.empty and feature_columns:
            # Fit scaler ONLY on train data
            self.scaler.fit(train_df[feature_columns])

        self._is_fitted = True
        return self.export_metadata()

    def transform(self, df: pd.DataFrame, split_name: MLSplitName) -> pd.DataFrame:
        self.validate_fit_state()

        if df.empty or not self.feature_columns:
            return df

        transformed_df = df.copy()

        if self.config.ml_dataset and self.config.ml_dataset.preprocessing.enabled:
             # Apply imputation (mocked for skeleton)
             if self.config.ml_dataset.preprocessing.imputation.enabled:
                 if self.config.ml_dataset.preprocessing.imputation.allow_ffill:
                     transformed_df[self.feature_columns] = transformed_df[self.feature_columns].ffill()

             # Apply clipping (mocked for skeleton)

             # Apply scaling
             transformed_df[self.feature_columns] = self.scaler.transform(transformed_df[self.feature_columns])

        return transformed_df

    def fit_transform_train(self, train_df: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
        self.fit_train(train_df, feature_columns)
        return self.transform(train_df, MLSplitName.TRAIN)

    def transform_validation(self, validation_df: pd.DataFrame) -> pd.DataFrame:
        return self.transform(validation_df, MLSplitName.VALIDATION)

    def transform_test(self, test_df: pd.DataFrame) -> pd.DataFrame:
        return self.transform(test_df, MLSplitName.TEST)

    def validate_fit_state(self) -> None:
        if not self._is_fitted:
            raise MLPreprocessingError("Pipeline must be fitted on train data before transforming.")

    def export_metadata(self) -> MLPreprocessorMetadata:
        preprocessing_config = self.config.ml_dataset.preprocessing if self.config.ml_dataset else None
        return MLPreprocessorMetadata(
            preprocessor_id="preprocessor_v1",
            scaler=preprocessing_config.scaler if preprocessing_config else "none",
            imputation_strategy=preprocessing_config.imputation.strategy if preprocessing_config else "none",
            clipping_method=preprocessing_config.clipping.method if preprocessing_config else "none",
            fit_split="train",
            fitted_columns=self.feature_columns,
            parameters=self.scaler.get_metadata(),
            fitted_at_utc=datetime.utcnow(),
            hash="dummy_hash_for_skeleton",
            warnings=[]
        )
