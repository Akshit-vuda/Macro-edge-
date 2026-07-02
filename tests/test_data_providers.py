"""
Tests for backend.services.data_providers.base — ABC contracts via Fake implementations.
"""

from datetime import datetime

import pandas as pd
import pytest

from backend.services.data_providers import (
    MarketDataProvider,
    NewsItem,
    NewsProvider,
    ScreenerProvider,
)


class FakeMarketDataProvider(MarketDataProvider):
    def get_bars(self, symbol: str, timeframe: str, start: str, end: str) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "ts": [datetime(2024, 1, 1)],
                "open": [1.0],
                "high": [1.5],
                "low": [0.5],
                "close": [1.2],
                "volume": [1000],
            }
        )


class FakeNewsProvider(NewsProvider):
    def get_news(self, symbols: list[str], since: datetime) -> list[NewsItem]:
        return [
            NewsItem(
                symbol=symbols[0],
                ts=datetime(2024, 1, 1),
                source="fake",
                headline="Fake headline",
                summary="Fake summary",
                url="https://example.com",
            )
        ]


class FakeScreenerProvider(ScreenerProvider):
    def screen(self, criteria: dict) -> pd.DataFrame:
        return pd.DataFrame({"symbol": ["AAPL", "MSFT"]})


def test_market_data_provider_get_bars() -> None:
    """FakeMarketDataProvider.get_bars returns the required OHLCV columns."""
    df = FakeMarketDataProvider().get_bars("AAPL", "1d", "2024-01-01", "2024-01-02")
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["ts", "open", "high", "low", "close", "volume"]


def test_news_provider_get_news() -> None:
    """FakeNewsProvider.get_news returns a list of NewsItem."""
    items = FakeNewsProvider().get_news(["AAPL"], datetime(2024, 1, 1))
    assert isinstance(items, list)
    assert len(items) == 1
    assert isinstance(items[0], NewsItem)
    assert items[0].symbol == "AAPL"


def test_screener_provider_screen() -> None:
    """FakeScreenerProvider.screen returns a DataFrame containing a 'symbol' column."""
    df = FakeScreenerProvider().screen({"min_volume": 1000})
    assert isinstance(df, pd.DataFrame)
    assert "symbol" in df.columns


@pytest.mark.parametrize(
    "abstract_cls",
    [MarketDataProvider, NewsProvider, ScreenerProvider],
)
def test_abstract_providers_cannot_be_instantiated(abstract_cls) -> None:
    """Each ABC raises TypeError when instantiated directly."""
    with pytest.raises(TypeError):
        abstract_cls()


def test_news_item_is_dataclass_with_expected_fields() -> None:
    """NewsItem exposes exactly the required fields."""
    item = NewsItem(
        symbol="AAPL",
        ts=datetime(2024, 1, 1),
        source="fake",
        headline="h",
        summary="s",
        url="u",
    )
    assert item.symbol == "AAPL"
    assert item.ts == datetime(2024, 1, 1)
    assert item.source == "fake"
    assert item.headline == "h"
    assert item.summary == "s"
    assert item.url == "u"
