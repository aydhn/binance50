with open("binance50/src/binance50/core/error_classifier.py", "r") as f:
    content = f.read()

import_statement = """
from binance50.core.exceptions import (
    Binance50Error,
    BinanceApiError,
    BinanceAuthenticationError,
    BinanceInsufficientBalanceError,
    BinanceIpBanError,
    BinancePermissionError,
    BinanceRateLimitError,
    BinanceServerError,
    BinanceSymbolFilterError,
    BinanceTimestampError,
    BinanceUnknownExecutionStatusError,
    StreamParseError,
    StreamStaleEventError,
    StreamDuplicateEventError,
    StreamBufferOverflowError,
    StreamRouteError,
    StreamConnectionDisabledError,
)
"""

if "StreamParseError" not in content:
    # replace imports
    import re
    content = re.sub(r'from binance50\.core\.exceptions import \([\s\S]*?\)', import_statement.strip(), content)

    # add stream classification
    classify_func = """
def classify_stream_error(msg: str) -> type[Binance50Error]:
    msg_lower = msg.lower()
    if "missing" in msg_lower or "invalid numeric" in msg_lower:
        return StreamParseError
    if "stale" in msg_lower:
        return StreamStaleEventError
    if "duplicate" in msg_lower:
        return StreamDuplicateEventError
    if "overflow" in msg_lower or "buffer full" in msg_lower:
        return StreamBufferOverflowError
    if "route" in msg_lower or "unsupported" in msg_lower:
        return StreamRouteError
    if "real connect disabled" in msg_lower or "disabled in phase 9" in msg_lower:
        return StreamConnectionDisabledError
    from binance50.core.exceptions import StreamError
    return StreamError
"""
    content = content + "\n" + classify_func

    with open("binance50/src/binance50/core/error_classifier.py", "w") as f:
        f.write(content)
