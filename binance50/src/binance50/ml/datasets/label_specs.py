from binance50.config.models import AppConfig
from binance50.core.exceptions import MLLabelSpecError
from binance50.ml.datasets.models import MLLabelSpec, MLLabelType


def build_default_label_specs(config: AppConfig) -> list[MLLabelSpec]:
    if not config.ml_dataset or not config.ml_dataset.labels.enabled:
        return []

    specs = []
    default_type = MLLabelType(config.ml_dataset.labels.default_label_type)

    for horizon in config.ml_dataset.labels.horizons_bars:
        spec = build_label_spec(default_type, horizon, config)
        specs.append(spec)

    return specs


def build_label_spec(label_type: MLLabelType, horizon_bars: int, config: AppConfig) -> MLLabelSpec:
    labels_config = config.ml_dataset.labels

    if horizon_bars <= 0:
        raise MLLabelSpecError("horizon_bars must be > 0")

    return MLLabelSpec(
        label_type=label_type,
        horizon_bars=horizon_bars,
        return_source=labels_config.return_source,
        threshold_pct=labels_config.classification_threshold_pct,
        neutral_zone_pct=labels_config.neutral_zone_pct,
        include_neutral_class=labels_config.include_neutral_class,
        label_column=f"{labels_config.label_column_prefix}{horizon_bars}h",
        future_return_column=f"{labels_config.future_return_column_prefix}{horizon_bars}h",
        description=f"{label_type.value} over {horizon_bars} bars",
    )


def validate_label_spec(spec: MLLabelSpec, config: AppConfig) -> None:
    if spec.horizon_bars <= 0:
        raise MLLabelSpecError(f"Invalid horizon {spec.horizon_bars}")

    if "label_" not in spec.label_column and "label_" not in spec.future_return_column:
         raise MLLabelSpecError("Label columns must be within the safe namespace prefix 'label_'")


def validate_label_specs(specs: list[MLLabelSpec], config: AppConfig) -> None:
    if not specs:
        return

    for spec in specs:
        validate_label_spec(spec, config)


def label_spec_to_report(spec: MLLabelSpec) -> dict:
    return {
        "label_type": spec.label_type.value,
        "horizon_bars": spec.horizon_bars,
        "label_column": spec.label_column,
        "future_return_column": spec.future_return_column
    }
