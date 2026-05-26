import re

with open("binance50/config/default.yaml", "r") as f:
    content = f.read()

ml_config = """
ml_dataset:
  enabled: true
  output_dataset_name: ml_datasets
  cache_enabled: true
  cache_dir: data/ml/datasets/cache
  export_dir: data/ml/datasets/exports
  registry_dir: data/ml/datasets/registry

  real_exchange_forbidden: true
  paper_trade_forbidden: true
  live_trade_forbidden: true
  order_creation_forbidden: true
  api_key_forbidden: true
  signed_request_forbidden: true
  dashboard_forbidden: true
  model_training_deferred: true
  prediction_deferred: true

  sources:
    use_indicator_v1: true
    use_indicator_v2: true
    use_strategy_candidates: false
    use_scored_signals: true
    use_regimes: true
    use_risk_assessments: true
    use_backtest_metadata: false
    use_walkforward_metadata: false
    require_source_hashes: true
    require_source_timestamps: true

  feature_selection:
    enabled: true
    include_prefixes:
      - trend_
      - mom_
      - vol_
      - volu_
      - tr_
      - div_
      - mtf_
      - pat_
      - reg_
      - signal_
      - risk_
    exclude_prefixes:
      - label_
      - target_
      - future_
      - next_
      - forward_
      - order_
      - execution_
    required_base_columns:
      - symbol
      - market_scope
      - interval
      - open_time
      - close_time
    max_feature_columns: 1500
    min_feature_columns: 10
    reject_all_nan_features: true
    reject_constant_features: false
    warn_constant_features: true
    max_nan_ratio_per_feature: 0.40
    max_inf_count: 0
    allow_object_features: false
    allow_boolean_features: true
    allow_categorical_features: true
    categorical_encoding_deferred: true

  labels:
    enabled: true
    default_label_type: forward_return_classification
    allowed_label_types:
      - forward_return_regression
      - forward_return_classification
      - volatility_adjusted_return_classification
      - triple_barrier_skeleton
      - ranking_skeleton
    horizons_bars:
      - 1
      - 3
      - 5
      - 10
      - 20
    default_horizon_bars: 5
    return_source: close
    classification_threshold_pct: 0.20
    neutral_zone_pct: 0.05
    include_neutral_class: true
    label_column_prefix: label_
    future_return_column_prefix: label_future_return_
    allow_label_columns_in_features: false
    drop_rows_without_label: true
    drop_last_horizon_rows: true
    triple_barrier:
      enabled: false
      profit_take_pct: 1.0
      stop_loss_pct: 0.5
      max_holding_bars: 20
      full_engine_deferred: true

  splits:
    enabled: true
    split_method: chronological
    train_pct: 0.60
    validation_pct: 0.20
    test_pct: 0.20
    min_train_rows: 500
    min_validation_rows: 200
    min_test_rows: 200
    time_series_cv_enabled: true
    time_series_cv_splits: 3
    embargo_bars: 0
    purge_overlapping_labels: true
    test_set_for_final_report_only: true
    reject_split_overlap: true
    reject_test_selection: true

  preprocessing:
    enabled: true
    fit_transform_train_only: true
    transform_validation_test_only: true
    scaler: standard
    allowed_scalers:
      - none
      - standard
      - robust
      - minmax
    imputation:
      enabled: true
      strategy: median_train_only
      allow_bfill: false
      allow_ffill: true
      fit_imputer_train_only: true
    clipping:
      enabled: true
      method: train_quantile
      lower_quantile: 0.001
      upper_quantile: 0.999
      fit_clipper_train_only: true
    categorical:
      enabled: false
      encoding_deferred: true
    persist_preprocessor: true
    preprocessor_registry_enabled: true

  alignment:
    enabled: true
    method: backward_asof
    reject_forward_alignment: true
    reject_nearest_alignment: true
    require_no_future_join: true
    tolerance_bars: 1
    require_closed_candles: true

  leakage:
    prevent_lookahead_bias: true
    reject_future_columns_in_features: true
    reject_target_columns_in_features: true
    reject_label_columns_in_features: true
    reject_next_columns_in_features: true
    reject_forward_columns_in_features: true
    reject_negative_shift_features: true
    allow_forward_shift_only_for_labels: true
    reject_global_scaler_fit: true
    reject_global_imputer_fit: true
    reject_global_clipper_fit: true
    reject_test_fit: true
    reject_validation_fit: true
    reject_same_bar_label_as_feature: true

  quality:
    reject_empty_dataset: true
    reject_missing_labels: true
    reject_missing_features: true
    reject_single_class_labels: false
    warn_single_class_labels: true
    warn_class_imbalance: true
    max_majority_class_ratio: 0.85
    reject_nan_inf_features: true
    reject_nan_inf_labels: true
    reject_missing_split_metadata: true
    reject_missing_hashes: true
    reject_leakage_warnings: true
    warn_low_row_count: true
    min_total_rows_warning: 1000

walkforward:
  enabled: true"""

content = content.replace("walkforward:\n  enabled: true", ml_config)

with open("binance50/config/default.yaml", "w") as f:
    f.write(content)
