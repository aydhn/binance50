import yaml
from pathlib import Path

config_path = Path("binance50/config/default.yaml")
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

if "ml_training" not in config:
    config["ml_training"] = {
        "enabled": True,
        "output_dataset_name": "ml_training_runs",
        "cache_enabled": True,
        "cache_dir": "data/ml/training/cache",
        "export_dir": "data/ml/training/exports",
        "registry_dir": "data/ml/training/registry",
        "artifacts_dir": "data/ml/training/artifacts",
        "reports_dir": "data/ml/training/reports",

        "real_exchange_forbidden": True,
        "paper_trade_forbidden": True,
        "live_trade_forbidden": True,
        "order_creation_forbidden": True,
        "api_key_forbidden": True,
        "signed_request_forbidden": True,
        "dashboard_forbidden": True,
        "prediction_serving_deferred": True,
        "execution_integration_forbidden": True,
        "auto_strategy_update_forbidden": True,

        "dataset": {
            "require_ml_dataset_manifest": True,
            "require_leakage_free_dataset": True,
            "require_quality_passed_dataset": True,
            "allowed_label_types": [
                "forward_return_classification",
                "forward_return_regression",
                "volatility_adjusted_return_classification"
            ],
            "default_label_column": "label_forward_return_classification_5",
            "require_split_metadata": True,
            "require_preprocessor_metadata": True,
            "reject_if_feature_contains_label": True,
            "reject_if_feature_contains_future": True,
            "reject_if_feature_contains_target": True,
            "reject_if_missing_train_validation_test": True
        },

        "task": {
            "default_task_type": "classification",
            "allowed_task_types": [
                "classification",
                "regression_skeleton"
            ],
            "multiclass_enabled": True,
            "binary_enabled": True,
            "regression_default_enabled": False,
            "ranking_deferred": True
        },

        "models": {
            "enabled_models": [
                "dummy_classifier",
                "logistic_regression",
                "random_forest_classifier",
                "hist_gradient_boosting_classifier"
            ],
            "default_model": "logistic_regression",
            "allow_regression_skeletons": True,
            "random_state": 42,
            "n_jobs": 1,
            "max_fit_seconds_per_model": 300,
            "max_models_per_run": 10,
            "allow_gpu": False,
            "require_deterministic_models": True,

            "logistic_regression": {
                "enabled": True,
                "max_iter": 1000,
                "class_weight": "balanced",
                "solver": "lbfgs",
                "C": 1.0
            },

            "random_forest_classifier": {
                "enabled": True,
                "n_estimators": 200,
                "max_depth": 6,
                "min_samples_leaf": 20,
                "class_weight": "balanced_subsample",
                "random_state": 42,
                "n_jobs": 1
            },

            "hist_gradient_boosting_classifier": {
                "enabled": True,
                "max_iter": 200,
                "max_leaf_nodes": 31,
                "learning_rate": 0.05,
                "l2_regularization": 0.0,
                "random_state": 42
            },

            "dummy_classifier": {
                "enabled": True,
                "strategy": "most_frequent"
            }
        },

        "validation": {
            "enabled": True,
            "method": "time_series_split",
            "use_existing_ml_splits": True,
            "train_split_name": "train",
            "validation_split_name": "validation",
            "test_split_name": "test",
            "time_series_cv_enabled": True,
            "time_series_cv_splits": 3,
            "test_set_final_report_only": True,
            "reject_test_selection": True,
            "reject_split_overlap": True,
            "require_chronological_order": True,
            "min_train_rows": 500,
            "min_validation_rows": 200,
            "min_test_rows": 200,
            "min_class_count_per_split": 2,
            "min_samples_per_class_warning": 25
        },

        "calibration": {
            "enabled": True,
            "calibrate_classifiers": True,
            "method": "sigmoid",
            "allowed_methods": [
                "sigmoid",
                "isotonic"
            ],
            "calibration_split": "validation",
            "fit_calibrator_on_test_forbidden": True,
            "require_calibration_report": True,
            "reliability_bins": 10,
            "compute_brier_score": True,
            "compute_expected_calibration_error": True,
            "warn_uncalibrated_probabilities": True,
            "isotonic_min_samples_warning": 1000
        },

        "metrics": {
            "classification": {
                "compute_accuracy": True,
                "compute_balanced_accuracy": True,
                "compute_precision_recall_f1": True,
                "compute_roc_auc": True,
                "compute_pr_auc": True,
                "compute_log_loss": True,
                "compute_brier_score": True,
                "compute_confusion_matrix": True,
                "compute_classification_report": True,
                "average": "weighted",
                "zero_division": 0
            },

            "regression": {
                "compute_mae": True,
                "compute_rmse": True,
                "compute_r2": True,
                "compute_directional_accuracy": True,
                "regression_deferred": True
            }
        },

        "feature_importance": {
            "enabled": True,
            "native_model_importance": True,
            "permutation_importance": True,
            "permutation_n_repeats": 5,
            "permutation_random_state": 42,
            "permutation_split": "validation",
            "max_features_reported": 100,
            "warn_high_cardinality_importance_bias": True
        },

        "overfit": {
            "enabled": True,
            "compare_train_validation": True,
            "max_train_validation_metric_gap": 0.25,
            "max_train_validation_auc_gap": 0.20,
            "warn_if_train_much_better": True,
            "reject_if_validation_worse_than_dummy": False,
            "warn_if_validation_worse_than_dummy": True,
            "warn_if_test_much_worse_than_validation": True,
            "test_degradation_warning_gap": 0.20
        },

        "registry": {
            "enabled": True,
            "active_model_serving_forbidden": True,
            "auto_promote_forbidden": True,
            "require_model_card": True,
            "require_training_manifest": True,
            "require_dataset_manifest_link": True,
            "require_reproducibility_hashes": True,
            "persist_model_artifacts": True,
            "artifact_format": "joblib",
            "persist_pickled_objects_warning": True,
            "allow_loading_untrusted_artifacts": False
        },

        "quality": {
            "reject_no_models_trained": True,
            "reject_all_models_failed": True,
            "reject_missing_metrics": True,
            "reject_missing_calibration_report": False,
            "reject_missing_model_card": True,
            "reject_missing_dataset_manifest": True,
            "reject_missing_hashes": True,
            "reject_nan_inf_metrics": True,
            "warn_low_sample_count": True,
            "warn_class_imbalance": True,
            "warn_single_class_split": True,
            "reject_single_class_train": True,
            "reject_single_class_validation": False,
            "warn_uncalibrated_model": True,
            "reject_live_or_paper_intent": True
        }
    }

    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

print("Updated config/default.yaml")
