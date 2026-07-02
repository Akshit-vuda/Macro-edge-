"""
Alpaca market data provider (alpaca-py, in-process).

Implements the B1 `MarketDataProvider` interface using the modern `alpaca-py`
SDK's `StockHistoricalDataClient`. Credentials come from `config.settings`
(ALPACA_API_KEY / ALPACA_SECRET_KEY). Defaults to the IEX feed so it works on
the free "Basic" market-data plan (SIP is the paid tier).

On missing credentials or any SDK/network error, methods log a warning and
return an empty DataFrame with the B1 columns — never raise.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

import pandas as pd
from alpaca.data.enums import DataFeed
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

from config import settings

from .base import MarketDataProvider

logger = logging.getLogger(__name__)

_BARS_COLUMNS = ["ts", "open", "high", "low", "close", "volume"]


def _to_timeframe(timeframe: str) -> TimeFrame:
    """Map a B1 timeframe string to an alpaca-py TimeFrame (defaults to daily)."""
    mapping = {
        "1m": TimeFrame(1, TimeFrameUnit.Minute),
        "5m": TimeFrame(5, TimeFrameUnit.Minute),
        "15m": TimeFrame(15, TimeFrameUnit.Minute),
        "30m": TimeFrame(30, TimeFrameUnit.Minute),
        "1h": TimeFrame(1, TimeFrameUnit.Hour),
        "1d": TimeFrame(1, TimeFrameUnit.Day),
    }
    return mapping.get(timeframe, TimeFrame(1, TimeFrameUnit.Day))


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    """Parse a date/datetime string to a datetime; None/empty -> None."""
    if not value:
        return None
    try:
        return pd.to_datetime(value).to_pydatetime()
    except (ValueError, TypeError):
        return None


class AlpacaDataProvider(MarketDataProvider):
    """Historical OHLCV bars from Alpaca via alpaca-py."""

    def __init__(
        self,
        client: Optional[StockHistoricalDataClient] = None,
        feed: DataFeed = DataFeed.IEX,
    ) -> None:
        """
        Args:
            client: injected StockHistoricalDataClient (for tests). If None, one
                is built from settings.ALPACA_API_KEY/SECRET_KEY when both are set.
            feed: market-data feed; defaults to IEX (free tier).
        """
        self.feed: DataFeed = feed
        if client is not None:
            self.client: Optional[StockHistoricalDataClient] = client
        elif settings.ALPACA_API_KEY and settings.ALPACA_SECRET_KEY:
            self.client = StockHistoricalDataClient(
                settings.ALPACA_API_KEY, settings.ALPACA_SECRET_KEY
            )
        else:
            self.client = None

    def get_bars(self, symbol: str, timeframe: str, start: str, end: str) -> pd.DataFrame:
        """
        Fetch historical OHLCV bars for a symbol (e.g. "AAPL").

        Args:
            symbol: ticker symbol.
            timeframe: one of 1m/5m/15m/30m/1h/1d (defaults to daily).
            start: inclusive start date "YYYY-MM-DD" (or datetime string).
            end: inclusive end date "YYYY-MM-DD" (or datetime string).

        Returns:
            DataFrame with columns ts, open, high, low, close, volume
            (empty on missing credentials or any error).
        """
        if self.client is None:
            logger.warning("Alpaca credentials not configured — returning empty bars for %s", symbol)
            return pd.DataFrame(columns=_BARS_COLUMNS)
        try:
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=_to_timeframe(timeframe),
                start=_parse_dt(start),
                end=_parse_dt(end),
                feed=self.feed,
            )
            bars = self.client.get_stock_bars(request)
        except Exception as exc:
            logger.warning("Alpaca get_stock_bars failed for %s: %s", symbol, exc)
            return pd.DataFrame(columns=_BARS_COLUMNS)
        return self._normalize_bars(bars)

    @staticmethod
    def _normalize_bars(bars) -> pd.DataFrame:
        """Map an alpaca-py BarSet to the B1 schema."""
        raw = getattr(bars, "df", None)
        if raw is None or raw.empty:
            return pd.DataFrame(columns=_BARS_COLUMNS)
        # alpaca-py indexes by (symbol, timestamp); flatten to columns.
        raw = raw.reset_index()
        out = pd.DataFrame(
            {
                "ts": pd.to_datetime(raw["timestamp"]),
                "open": raw["open"].astype(float),
                "high": raw["high"].astype(float),
                "low": raw["low"].astype(float),
                "close": raw["close"].astype(float),
                "volume": raw["volume"].astype("int64"),
            }
        )
        return out[_BARS_COLUMNS]
