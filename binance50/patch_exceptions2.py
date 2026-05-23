with open("src/binance50/core/exceptions.py") as f:
    content = f.read()

import re

# Redaction logic inside Binance50Error
new_methods = """
    def with_context(self, **kwargs: Any) -> "Binance50Error":
        self.metadata.update(kwargs)
        return self

    def safe_message(self) -> str:
        from binance50.logging.redaction import redact_text
        return redact_text(self.message)

    def to_dict(self, redacted: bool = True) -> dict[str, Any]:
        d = {
            "error_code": self.error_code,
            "message": self.safe_message() if redacted else self.message,
            "component": self.component,
            "severity": self.severity,
            "retryable": self.retryable,
            "user_action_required": self.user_action_required,
            "metadata": self.metadata.copy(),
        }
        if redacted:
            from binance50.logging.redaction import redact_dict
            d["metadata"] = redact_dict(d["metadata"])
        return d
"""

content = re.sub(
    r"    def to_dict\(self, redacted: bool = True\) -> dict\[str, Any\]:[\s\S]*?        }",
    new_methods,
    content,
    count=1,
)

with open("src/binance50/core/exceptions.py", "w") as f:
    f.write(content)
