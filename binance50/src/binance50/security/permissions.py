from dataclasses import dataclass

from binance50.config.models import AppConfig


@dataclass
class ApiPermissionSnapshot:
    permission_read: bool
    permission_spot_trade: bool
    permission_futures_trade: bool
    permission_margin_trade: bool
    ip_restricted: bool
    allowed_ips: list[str]

    @classmethod
    def from_config(cls, config: AppConfig) -> "ApiPermissionSnapshot":
        binance_creds = config.credentials.binance
        return cls(
            permission_read=binance_creds.permission_read,
            permission_spot_trade=binance_creds.permission_spot_trade,
            permission_futures_trade=binance_creds.permission_futures_trade,
            permission_margin_trade=binance_creds.permission_margin_trade,
            ip_restricted=binance_creds.ip_restricted,
            allowed_ips=binance_creds.allowed_ips.copy(),
        )

    def has_read(self) -> bool:
        return self.permission_read

    def has_spot_trade(self) -> bool:
        return self.permission_spot_trade

    def has_futures_trade(self) -> bool:
        return self.permission_futures_trade

    def has_margin_trade(self) -> bool:
        return self.permission_margin_trade

    def is_ip_restricted(self) -> bool:
        return self.ip_restricted

    def allowed_ips_count(self) -> int:
        return len(self.allowed_ips)
