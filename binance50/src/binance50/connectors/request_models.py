from typing import Any

from pydantic import BaseModel, Field

from binance50.core.enums import EndpointRole
from binance50.core.network import HttpMethod


class ConnectorRequest(BaseModel):
    request_id: str
    timestamp_utc: str
    method: HttpMethod
    path: str
    params: dict[str, Any] | None = None
    headers: dict[str, str] = Field(default_factory=dict)
    signed: bool = False
    endpoint_role: EndpointRole = EndpointRole.REST_PRIMARY
    weight: int = Field(default=1, ge=0)
    timeout_seconds: float = 10.0
    recv_window_ms: int = 5000
    correlation_id: str | None = None
    metadata: dict[str, Any] | None = None

    def redacted_dump(self) -> dict[str, Any]:
        d = self.model_dump()
        if d.get("headers"):
            d["headers"] = {"REDACTED": "true"}
        if d.get("params") and "signature" in d["params"]:
            d["params"]["signature"] = "REDACTED"
        return d
