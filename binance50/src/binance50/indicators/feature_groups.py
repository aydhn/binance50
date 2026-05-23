import pandas as pd
from typing import List, Dict, Optional
from pydantic import BaseModel
from binance50.config.models import AppConfig
from binance50.core.exceptions import FeatureGroupError
from binance50.features.grouping import exclude_non_feature_columns

class FeatureGroup(BaseModel):
    group_name: str
    prefixes: List[str]
    columns: List[str]
    required: bool = False
    description: str = ""
    metadata: Dict = {}

class FeatureGroupReport(BaseModel):
    total_features: int
    grouped_features: int
    ungrouped_features: int
    groups: Dict[str, List[str]]
    warnings: List[str] = []

def infer_feature_group(column_name: str, config: AppConfig) -> Optional[str]:
    cfg = config.indicator_v2.feature_groups
    if not cfg.enabled:
        return None

    for group_name, group_info in cfg.groups.items():
        prefixes = group_info.get("prefixes", [])
        if any(column_name.startswith(p) for p in prefixes):
            return group_name

    return None

def build_feature_groups(df: pd.DataFrame, config: AppConfig) -> List[FeatureGroup]:
    cfg = config.indicator_v2.feature_groups
    if not cfg.enabled:
        return []

    all_features = exclude_non_feature_columns(df.columns.tolist())

    group_objs = []

    for group_name, group_info in cfg.groups.items():
        prefixes = group_info.get("prefixes", [])
        cols = [c for c in all_features if any(c.startswith(p) for p in prefixes)]

        group_objs.append(FeatureGroup(
            group_name=group_name,
            prefixes=prefixes,
            columns=cols
        ))

    validate_feature_groups(group_objs, df, config)

    return group_objs

def validate_feature_groups(groups: List[FeatureGroup], df: pd.DataFrame, config: AppConfig) -> None:
    cfg = config.indicator_v2.feature_groups

    all_features = set(exclude_non_feature_columns(df.columns.tolist()))
    grouped_features = set()

    for g in groups:
        grouped_features.update(g.columns)

    ungrouped = all_features - grouped_features

    if ungrouped and not cfg.allow_ungrouped_features:
        raise FeatureGroupError(f"Found {len(ungrouped)} ungrouped features and allow_ungrouped_features is False. First few: {list(ungrouped)[:5]}")

def build_feature_group_report(df: pd.DataFrame, config: AppConfig) -> FeatureGroupReport:
    groups = build_feature_groups(df, config)
    all_features = exclude_non_feature_columns(df.columns.tolist())

    group_map = {g.group_name: g.columns for g in groups}
    grouped_count = sum(len(g.columns) for g in groups)
    ungrouped_count = len(all_features) - grouped_count

    return FeatureGroupReport(
        total_features=len(all_features),
        grouped_features=grouped_count,
        ungrouped_features=ungrouped_count,
        groups=group_map
    )

def add_feature_group_metadata(metadata: dict, groups: List[FeatureGroup]) -> dict:
    meta = metadata.copy()
    meta["groups"] = [g.model_dump() for g in groups]
    return meta
