from threading import Lock

from binance50.streams.event_types import StreamType
from binance50.streams.models import (
    BookTickerStreamEvent,
    KlineStreamEvent,
    MiniTickerStreamEvent,
    StreamEvent,
    TickerStreamEvent,
)


class RealtimeMarketDataStore:
    def __init__(self) -> None:
        self._book_tickers: dict[str, BookTickerStreamEvent] = {}
        self._tickers: dict[str, TickerStreamEvent | MiniTickerStreamEvent] = {}
        self._closed_klines: dict[tuple[str, str], KlineStreamEvent] = {}
        self._open_klines: dict[tuple[str, str], KlineStreamEvent] = {}
        self._lock = Lock()

    def update_from_event(self, event: StreamEvent) -> None:
        with self._lock:
            sym = event.symbol.upper()
            st = event.stream_type

            if st == StreamType.book_ticker and isinstance(event, BookTickerStreamEvent):
                self._book_tickers[sym] = event
            elif st in (StreamType.ticker, StreamType.mini_ticker) and isinstance(
                event, (TickerStreamEvent, MiniTickerStreamEvent)
            ):
                self._tickers[sym] = event
            elif st == StreamType.kline and isinstance(event, KlineStreamEvent):
                key = (sym, event.interval)
                if event.is_closed:
                    self._closed_klines[key] = event
                else:
                    self._open_klines[key] = event

    def get_latest_book_ticker(self, symbol: str) -> BookTickerStreamEvent | None:
        with self._lock:
            return self._book_tickers.get(symbol.upper())

    def get_latest_ticker(self, symbol: str) -> TickerStreamEvent | MiniTickerStreamEvent | None:
        with self._lock:
            return self._tickers.get(symbol.upper())

    def get_latest_closed_kline(self, symbol: str, interval: str) -> KlineStreamEvent | None:
        with self._lock:
            return self._closed_klines.get((symbol.upper(), interval))

    def get_latest_open_kline(self, symbol: str, interval: str) -> KlineStreamEvent | None:
        with self._lock:
            return self._open_klines.get((symbol.upper(), interval))

    def list_symbols(self) -> list[str]:
        with self._lock:
            syms = set()
            syms.update(self._book_tickers.keys())
            syms.update(self._tickers.keys())
            for s, _ in self._closed_klines:
                syms.add(s)
            for s, _ in self._open_klines:
                syms.add(s)
            return sorted(syms)

    def to_snapshot(self) -> dict:
        with self._lock:
            return {
                "book_tickers_count": len(self._book_tickers),
                "tickers_count": len(self._tickers),
                "closed_klines_count": len(self._closed_klines),
                "open_klines_count": len(self._open_klines),
                "symbols": self.list_symbols(),
            }

    def clear(self) -> None:
        with self._lock:
            self._book_tickers.clear()
            self._tickers.clear()
            self._closed_klines.clear()
            self._open_klines.clear()
