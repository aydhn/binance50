import pytest
from typer.testing import CliRunner
from binance50.cli import app

runner = CliRunner()

def test_ml_training_config():
    result = runner.invoke(app, ["ml-training-config"])
    assert result.exit_code == 0
    assert "Prediction serving" in result.stdout

def test_ml_training_models():
    result = runner.invoke(app, ["ml-training-models"])
    assert result.exit_code == 0
    assert "Enabled Models" in result.stdout

def test_ml_train_fixture_dataset():
    result = runner.invoke(app, ["ml-train-fixture-dataset"])
    assert result.exit_code == 0

def test_ml_model_comparison():
    result = runner.invoke(app, ["ml-model-comparison"])
    assert result.exit_code == 0

def test_ml_calibration_report():
    result = runner.invoke(app, ["ml-calibration-report"])
    assert result.exit_code == 0

def test_ml_feature_importance():
    result = runner.invoke(app, ["ml-feature-importance"])
    assert result.exit_code == 0

def test_ml_model_card():
    result = runner.invoke(app, ["ml-model-card"])
    assert result.exit_code == 0

def test_ml_model_registry():
    result = runner.invoke(app, ["ml-model-registry"])
    assert result.exit_code == 0

def test_ml_training_quality_check():
    result = runner.invoke(app, ["ml-training-quality-check"])
    assert result.exit_code == 0

def test_ml_training_safety_check():
    result = runner.invoke(app, ["ml-training-safety-check"])
    assert result.exit_code == 0

def test_ml_model_leakage_check():
    result = runner.invoke(app, ["ml-model-leakage-check"])
    assert result.exit_code == 0

def test_doctor():
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "prediction serving deferred: True" in result.stdout
