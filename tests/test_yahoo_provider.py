"""
Tests for the yfinance + RSS news provider (B2).

yfinance.Ticker is monkeypatched; feedparser is mocked/skippable.
"""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from backend.services.data_providers.base import NewsItem, NewsProvider
from backend.services.data_providers.yahoo_provider import YahooNewsProvider

MODULE = "backend.services.data_providers.yahoo_provider"


def _nested_shape_news() -> list:
    return [
        {
            "content": {
                "title": "Apple hits new high",
                "summary": "Shares climbed today.",
                "pubDate": "2026-07-01T12:00:00Z",
                "canonicalUrl": {"url": "https://example.com/apple-high"},
                "provider": {"displayName": "Example News"},
            }
        }
    ]


def _flat_shape_news() -> list:
    return [
        {
            "title": "Apple beats earnings",
            "publisher": "Old Wire",
            "link": "https://example.com/apple-earnings",
            "providerPublishTime": int(datetime(2026, 7, 1, 12, 0, tzinfo=timezone.utc).timestamp()),
        }
    ]


def test_provider_implements_b1_interface() -> None:
    assert issubclass(YahooNewsProvider, NewsProvider)


def test_get_news_nested_shape() -> None:
    fake_ticker = SimpleNamespace(news=_nested_shape_news())
    since = datetime(2026, 6, 1, tzinfo=timezone.utc)
    with patch(f"{MODULE}.yfinance.Ticker", return_value=fake_ticker), patch(
        f"{MODULE}.YahooNewsProvider._get_rss_news", return_value=[]
    ):
        items = YahooNewsProvider().get_news(["AAPL"], since)
    assert len(items) == 1
    item = items[0]
    assert isinstance(item, NewsItem)
    assert item.symbol == "AAPL"
    assert item.headline == "Apple hits new high"
    assert item.summary == "Shares climbed today."
    assert item.source == "Example News"
    assert item.url == "https://example.com/apple-high"
    assert item.ts.tzinfo is not None


def test_get_news_flat_shape() -> None:
    fake_ticker = SimpleNamespace(news=_flat_shape_news())
    since = datetime(2026, 6, 1, tzinfo=timezone.utc)
    with patch(f"{MODULE}.yfinance.Ticker", return_value=fake_ticker), patch(
        f"{MODULE}.YahooNewsProvider._get_rss_news", return_value=[]
    ):
        items = YahooNewsProvider().get_news(["AAPL"], since)
    assert len(items) == 1
    item = items[0]
    assert item.symbol == "AAPL"
    assert item.headline == "Apple beats earnings"
    assert item.source == "Old Wire"
    assert item.url == "https://example.com/apple-earnings"


def test_get_news_filters_by_since() -> None:
    fake_ticker = SimpleNamespace(news=_nested_shape_news())
    since = datetime(2026, 7, 2, tzinfo=timezone.utc)  # after the fake item's pubDate
    with patch(f"{MODULE}.yfinance.Ticker", return_value=fake_ticker), patch(
        f"{MODULE}.YahooNewsProvider._get_rss_news", return_value=[]
    ):
        items = YahooNewsProvider().get_news(["AAPL"], since)
    assert items == []


def test_get_news_accepts_naive_since_no_raise() -> None:
    # A tz-naive `since` must not raise (aware-vs-naive) — the guard coerces to UTC.
    fake_ticker = SimpleNamespace(news=_nested_shape_news())
    naive_since = datetime(2026, 6, 1)  # no tzinfo
    with patch(f"{MODULE}.yfinance.Ticker", return_value=fake_ticker), patch(
        f"{MODULE}.YahooNewsProvider._get_rss_news", return_value=[]
    ):
        items = YahooNewsProvider().get_news(["AAPL"], naive_since)
    assert len(items) == 1  # item pubDate 2026-07-01 is after 2026-06-01


def test_get_news_ticker_raises_returns_empty_no_raise() -> None:
    with patch(f"{MODULE}.yfinance.Ticker", side_effect=RuntimeError("boom")), patch(
        f"{MODULE}.YahooNewsProvider._get_rss_news", return_value=[]
    ):
        items = YahooNewsProvider().get_news(["AAPL"], datetime(2026, 6, 1, tzinfo=timezone.utc))
    assert items == []


def test_get_news_includes_rss_items() -> None:
    since = datetime(2026, 6, 1, tzinfo=timezone.utc)
    rss_item = NewsItem(
        symbol="",
        ts=datetime(2026, 7, 1, tzinfo=timezone.utc),
        source="Reuters",
        headline="Markets rally",
        summary="Broad rally today.",
        url="https://example.com/rally",
    )
    with patch(f"{MODULE}.yfinance.Ticker", return_value=SimpleNamespace(news=[])), patch(
        f"{MODULE}.YahooNewsProvider._get_rss_news", return_value=[rss_item]
    ):
        items = YahooNewsProvider().get_news(["AAPL"], since)
    assert rss_item in items


def test_rss_feedparser_missing_skips_gracefully() -> None:
    provider = YahooNewsProvider()
    with patch.dict("sys.modules", {"feedparser": None}):
        items = provider._get_rss_news(datetime(2026, 6, 1, tzinfo=timezone.utc))
    assert items == []


def test_rss_parses_entries_and_filters_since() -> None:
    provider = YahooNewsProvider()
    fake_feed = SimpleNamespace(
        feed=SimpleNamespace(title="Reuters Business"),
        entries=[
            SimpleNamespace(
                title="Old news",
                summary="stale",
                link="https://example.com/old",
                published_parsed=(2026, 1, 1, 0, 0, 0, 0, 0, 0),
            ),
            SimpleNamespace(
                title="Fresh news",
                summary="hot off the press",
                link="https://example.com/fresh",
                published_parsed=(2026, 7, 1, 0, 0, 0, 0, 0, 0),
            ),
        ],
    )
    fake_feedparser = MagicMock()
    fake_feedparser.parse.return_value = fake_feed
    with patch(f"{MODULE}.settings.RSS_FEEDS", ["https://example.com/feed"]), patch.dict(
        "sys.modules", {"feedparser": fake_feedparser}
    ):
        items = provider._get_rss_news(datetime(2026, 6, 1, tzinfo=timezone.utc))
    assert len(items) == 1
    assert items[0].symbol == ""
    assert items[0].headline == "Fresh news"
    assert items[0].source == "Reuters Business"
    assert items[0].url == "https://example.com/fresh"
