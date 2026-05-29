with open("binance50/src/binance50/core/error_classifier.py", "r") as f:
    content = f.read()

new_logic = """
def is_portfolio_sandbox_error(error: Exception) -> bool:
    from binance50.core.exceptions import PortfolioSandboxError
    return isinstance(error, PortfolioSandboxError)

def classify_portfolio_error(error_message: str) -> str:
    from binance50.core.error_codes import (
        PORTFOLIO_CANDIDATE_INPUT_FAILED,
        PORTFOLIO_CORRELATION_FAILED,
        PORTFOLIO_EXPOSURE_FAILED,
        PORTFOLIO_CONCENTRATION_FAILED,
        PORTFOLIO_INTEGRATION_FORBIDDEN,
        PORTFOLIO_OPTIMIZER_SKELETON_FAILED,
        PORTFOLIO_SANDBOX_QUALITY_FAILED,
        PORTFOLIO_SANDBOX_CONFIG_INVALID
    )
    msg = error_message.lower()

    if "missing candidates" in msg:
        return PORTFOLIO_CANDIDATE_INPUT_FAILED
    if "future correlation" in msg or "invalid correlation matrix" in msg:
        return PORTFOLIO_CORRELATION_FAILED
    if "exposure violation" in msg:
        return PORTFOLIO_EXPOSURE_FAILED
    if "high concentration" in msg:
        return PORTFOLIO_CONCENTRATION_FAILED
    if "production write attempt" in msg:
        return PORTFOLIO_INTEGRATION_FORBIDDEN
    if "production allocation" in msg:
        return PORTFOLIO_OPTIMIZER_SKELETON_FAILED
    if "missing breakdown" in msg:
        return PORTFOLIO_SANDBOX_QUALITY_FAILED

    return PORTFOLIO_SANDBOX_CONFIG_INVALID
"""
content += new_logic

with open("binance50/src/binance50/core/error_classifier.py", "w") as f:
    f.write(content)
