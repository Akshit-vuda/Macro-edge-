"""
Data Provider Interfaces
Abstract base classes that market data, news, and screener providers must implement.
Strategy/risk code talks to vendors only through these interfaces.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

import pandas as pd


@dataclass
class NewsItem:
    """A single news item normalized across providers."""
    symbol: str
    ts: datetime
    source: str
    headline: str
    summary: str
    url: str


class MarketDataProvider(ABC):
    """Source of historical/live OHLCV bars."""

    @abstractmethod
    def get_bars(self, symbol: str, timeframe: str, start: str, end: str) -> pd.DataFrame:
        """
        Fetch OHLCV bars for a symbol.

        Returns a DataFrame with columns: ts, open, high, low, close, volume.
        """
        ...


class NewsProvider(ABC):
    """Source of news items for a set of symbols."""

    @abstractmethod
    def get_news(self, symbols: list[str], since: datetime) -> list[NewsItem]:
        """Fetch news items for the given symbols published at or after `since`."""
        ...


class ScreenerProvider(ABC):
    """Source of screened symbol lists matching criteria."""

    @abstractmethod
    def screen(self, criteria: dict) -> pd.DataFrame:
        """
        Screen symbols by criteria.

        Returns a DataFrame with columns including 'symbol'.
        """
        ...
