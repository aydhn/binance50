from typing import Any

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.core.exceptions import PortfolioCovarianceError


class PortfolioCovarianceReport(BaseModel):
    run_id: str
    method: str
    symbols: list[str]
    covariance_matrix: dict[str, dict[str, float]]
    annualization_periods: int
    non_finite_count: int
    symmetric: bool
    positive_semidefinite_warning: bool
    regularization_applied: bool
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

def compute_sample_covariance(returns_df: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
    if returns_df.empty:
        return pd.DataFrame()
    cov_df = returns_df.cov()
    annualization_factor = config.portfolio_construction.covariance.annualization_periods
    cov_df = cov_df * annualization_factor
    return cov_df

def regularize_covariance(cov_df: pd.DataFrame, epsilon: float) -> pd.DataFrame:
    if cov_df.empty: return cov_df
    reg_cov = cov_df.copy()
    np.fill_diagonal(reg_cov.values, reg_cov.values.diagonal() + epsilon)
    return reg_cov

def check_covariance_symmetric(cov_df: pd.DataFrame, atol: float = 1e-8) -> bool:
    if cov_df.empty: return True
    return np.allclose(cov_df.values, cov_df.values.T, atol=atol)

def check_covariance_positive_semidefinite(cov_df: pd.DataFrame) -> bool:
    if cov_df.empty: return True
    try:
        eigenvalues = np.linalg.eigvalsh(cov_df.values)
        return bool(np.all(eigenvalues >= -1e-8))
    except np.linalg.LinAlgError:
        return False

def validate_covariance_matrix(cov_df: pd.DataFrame, config: AppConfig) -> None:
    if cov_df.empty: return
    if config.portfolio_construction.covariance.reject_non_finite_covariance and not np.isfinite(cov_df.values).all():
        raise PortfolioCovarianceError("Covariance matrix contains non-finite values (NaN or Inf).")
    if config.portfolio_construction.covariance.reject_non_symmetric_covariance and not check_covariance_symmetric(cov_df):
        raise PortfolioCovarianceError("Covariance matrix is not symmetric.")

def build_covariance_report(cov_df: pd.DataFrame, config: AppConfig, run_id: str = "unknown") -> PortfolioCovarianceReport:
    warnings = []
    is_symmetric = check_covariance_symmetric(cov_df)
    is_psd = check_covariance_positive_semidefinite(cov_df)

    if not is_psd and config.portfolio_construction.covariance.warn_non_positive_semidefinite:
        warnings.append("Covariance matrix is not positive semi-definite.")

    non_finite_count = int(np.sum(~np.isfinite(cov_df.values)))

    cov_dict = {}
    if not cov_df.empty:
        cov_filled = cov_df.where(pd.notnull(cov_df), None)
        cov_dict = {col: cov_filled[col].to_dict() for col in cov_filled.columns}

    return PortfolioCovarianceReport(
        run_id=run_id,
        method=config.portfolio_construction.covariance.method,
        symbols=list(cov_df.columns),
        covariance_matrix=cov_dict,
        annualization_periods=config.portfolio_construction.covariance.annualization_periods,
        non_finite_count=non_finite_count,
        symmetric=is_symmetric,
        positive_semidefinite_warning=not is_psd,
        regularization_applied=False,
        warnings=warnings
    )
