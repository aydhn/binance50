from pydantic import BaseModel

from binance50.core.enums import AccountDomain, ExchangeName, MarketScope


class ConnectorCapabilities(BaseModel):
    exchange: ExchangeName
    account_domain: AccountDomain
    market_scope: MarketScope
    supports_rest: bool = False
    supports_websocket_market: bool = False
    supports_websocket_user: bool = False
    supports_testnet: bool = False
    supports_mainnet: bool = False
    supports_readonly: bool = False
    supports_market_data: bool = False
    supports_account_data: bool = False
    supports_order_placement: bool = False
    supports_paper_mode: bool = False
    supports_user_data_stream: bool = False
    supports_combined_streams: bool = False
    supports_raw_streams: bool = False
    supports_routed_futures_streams: bool = False

    order_placement_enabled: bool = False
    connection_enabled: bool = False
    websocket_enabled: bool = False
    user_data_stream_enabled: bool = False
    notes: str | None = None
