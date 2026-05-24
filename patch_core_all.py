import re

# Update error_codes.py
with open("binance50/src/binance50/core/error_codes.py", "r") as f:
    content = f.read()

new_error_codes = """
    # Risk Engine Errors
    RISK_CONFIG_INVALID = "RISK_CONFIG_INVALID"
    RISK_VALIDATION_FAILED = "RISK_VALIDATION_FAILED"
    RISK_POLICY_FAILED = "RISK_POLICY_FAILED"
    RISK_ASSESSMENT_FAILED = "RISK_ASSESSMENT_FAILED"
    RISK_QUALITY_FAILED = "RISK_QUALITY_FAILED"
    RISK_CACHE_FAILED = "RISK_CACHE_FAILED"
    RISK_LIMIT_EXCEEDED = "RISK_LIMIT_EXCEEDED"
    RISK_EXPOSURE_FAILED = "RISK_EXPOSURE_FAILED"
    RISK_NOTIONAL_FAILED = "RISK_NOTIONAL_FAILED"
    RISK_FILTER_FAILED = "RISK_FILTER_FAILED"
    RISK_LEVERAGE_FAILED = "RISK_LEVERAGE_FAILED"
    RISK_FREQUENCY_FAILED = "RISK_FREQUENCY_FAILED"
    RISK_EXECUTION_FORBIDDEN = "RISK_EXECUTION_FORBIDDEN"
    RISK_ORDER_OBJECT_DETECTED = "RISK_ORDER_OBJECT_DETECTED"
"""
if "RISK_CONFIG_INVALID" not in content:
    content = content.replace("class ErrorCode(str, Enum):", "class ErrorCode(str, Enum):\n" + new_error_codes)
    with open("binance50/src/binance50/core/error_codes.py", "w") as f:
        f.write(content)

# Update exceptions.py
with open("binance50/src/binance50/core/exceptions.py", "r") as f:
    content = f.read()

if "RiskConfigError" in content:
    # Fix the init
    content = re.sub(
        r'class RiskConfigError.*?class RiskValidationError',
        '''class RiskConfigError(RiskError):
    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message, ErrorCode.RISK_CONFIG_INVALID, details)

class RiskValidationError''',
        content,
        flags=re.DOTALL
    )
    content = re.sub(r'class RiskValidationError.*?class RiskPolicyError', '''class RiskValidationError(RiskError):
    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message, ErrorCode.RISK_VALIDATION_FAILED, details)

class RiskPolicyError''', content, flags=re.DOTALL)

    content = re.sub(r'class RiskPolicyError.*?class RiskAssessmentError', '''class RiskPolicyError(RiskError):
    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message, ErrorCode.RISK_POLICY_FAILED, details)

class RiskAssessmentError''', content, flags=re.DOTALL)

    content = re.sub(r'class RiskAssessmentError.*?class RiskQualityError', '''class RiskAssessmentError(RiskError):
    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message, ErrorCode.RISK_ASSESSMENT_FAILED, details)

class RiskQualityError''', content, flags=re.DOTALL)

    content = re.sub(r'class RiskQualityError.*?class RiskCacheError', '''class RiskQualityError(RiskError):
    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message, ErrorCode.RISK_QUALITY_FAILED, details)

class RiskCacheError''', content, flags=re.DOTALL)

    content = re.sub(r'class RiskCacheError.*?class RiskLimitError', '''class RiskCacheError(RiskError):
    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message, ErrorCode.RISK_CACHE_FAILED, details)

class RiskLimitError''', content, flags=re.DOTALL)

    content = re.sub(r'class RiskLimitError.*?class RiskExposureError', '''class RiskLimitError(RiskError):
    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message, ErrorCode.RISK_LIMIT_EXCEEDED, details)

class RiskExposureError''', content, flags=re.DOTALL)

    content = re.sub(r'class RiskExposureError.*?class RiskNotionalError', '''class RiskExposureError(RiskError):
    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message, ErrorCode.RISK_EXPOSURE_FAILED, details)

class RiskNotionalError''', content, flags=re.DOTALL)

    content = re.sub(r'class RiskNotionalError.*?class RiskFilterError', '''class RiskNotionalError(RiskError):
    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message, ErrorCode.RISK_NOTIONAL_FAILED, details)

class RiskFilterError''', content, flags=re.DOTALL)

    content = re.sub(r'class RiskFilterError.*?class RiskLeverageError', '''class RiskFilterError(RiskError):
    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message, ErrorCode.RISK_FILTER_FAILED, details)

class RiskLeverageError''', content, flags=re.DOTALL)

    content = re.sub(r'class RiskLeverageError.*?class RiskFrequencyError', '''class RiskLeverageError(RiskError):
    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message, ErrorCode.RISK_LEVERAGE_FAILED, details)

class RiskFrequencyError''', content, flags=re.DOTALL)

    content = re.sub(r'class RiskFrequencyError.*?class RiskExecutionForbiddenError', '''class RiskFrequencyError(RiskError):
    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message, ErrorCode.RISK_FREQUENCY_FAILED, details)

class RiskExecutionForbiddenError''', content, flags=re.DOTALL)

    content = re.sub(r'class RiskExecutionForbiddenError.*?class RiskOrderObjectDetectedError', '''class RiskExecutionForbiddenError(RiskError):
    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message, ErrorCode.RISK_EXECUTION_FORBIDDEN, details)

class RiskOrderObjectDetectedError''', content, flags=re.DOTALL)

    content = re.sub(r'class RiskOrderObjectDetectedError.*?$', '''class RiskOrderObjectDetectedError(RiskError):
    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message, ErrorCode.RISK_ORDER_OBJECT_DETECTED, details)
''', content, flags=re.DOTALL)

    with open("binance50/src/binance50/core/exceptions.py", "w") as f:
        f.write(content)
