# Just verifying that the CLI can load without errors
# (the detailed runtime checks are performed by check_project.py)
def test_cli_import():
    try:
        _ = __import__("binance50.cli")
    except ImportError as e:
        import pytest

        pytest.fail(f"Could not import CLI: {e}")
