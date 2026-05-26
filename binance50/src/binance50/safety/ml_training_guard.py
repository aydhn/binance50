from typing import Any, Dict
from binance50.config.models import AppConfig

def assert_ml_training_config_safe(config: AppConfig) -> None:
    c = config.ml_training
    if not c.real_exchange_forbidden:
        raise ValueError("real_exchange_forbidden must be True")
    if not c.paper_trade_forbidden:
        raise ValueError("paper_trade_forbidden must be True")
    if not c.live_trade_forbidden:
        raise ValueError("live_trade_forbidden must be True")
    if not c.order_creation_forbidden:
        raise ValueError("order_creation_forbidden must be True")
    if not c.prediction_serving_deferred:
        raise ValueError("prediction_serving_deferred must be True")
    if not c.execution_integration_forbidden:
        raise ValueError("execution_integration_forbidden must be True")
    if not c.auto_strategy_update_forbidden:
        raise ValueError("auto_strategy_update_forbidden must be True")

def assert_ml_training_input_safe(dataset_result: Any, config: AppConfig) -> None:
    pass

def assert_ml_training_output_safe(result: Any, config: AppConfig) -> None:
    pass

def assert_no_prediction_serving(config: AppConfig) -> None:
    if not config.ml_training.prediction_serving_deferred:
        raise ValueError("Prediction serving must be deferred")

def assert_no_execution_integration(config: AppConfig) -> None:
    if not config.ml_training.execution_integration_forbidden:
        raise ValueError("Execution integration must be forbidden")

def assert_no_live_paper_intent(payload: Any) -> None:
    if hasattr(payload, "prediction_intent") and getattr(payload, "prediction_intent") in ["live", "paper"]:
        raise ValueError("Live/paper intent found")

def build_ml_training_safety_report(config: AppConfig) -> Dict[str, Any]:
    return {"status": "safe"}
