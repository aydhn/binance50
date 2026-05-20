from typing import Any, Protocol

from binance50.core.exceptions import OrderPathDisabledError


class OrderGatewayProtocol(Protocol):
    def is_enabled(self) -> bool: ...
    def submit_order(self, *args: Any, **kwargs: Any) -> Any: ...
    def cancel_order(self, *args: Any, **kwargs: Any) -> Any: ...
    def close_position(self, *args: Any, **kwargs: Any) -> Any: ...


class DisabledOrderGateway:
    def is_enabled(self) -> bool:
        return False

    def submit_order(self, *args: Any, **kwargs: Any) -> Any:
        raise OrderPathDisabledError("Order gateway is disabled")

    def cancel_order(self, *args: Any, **kwargs: Any) -> Any:
        raise OrderPathDisabledError("Order gateway is disabled")

    def close_position(self, *args: Any, **kwargs: Any) -> Any:
        raise OrderPathDisabledError("Order gateway is disabled")
