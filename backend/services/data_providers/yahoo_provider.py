"""
yfinance + RSS news provider.

Implements the B1 `NewsProvider` interface. Two sources are merged:
  1. yfinance.Ticker(symbol).news — per-symbol headlines (handles both the
     newer nested `item["content"]` shape and the older flat shape).
  2. RSS feeds from config.settings.RSS_FEEDS — market-wide, symbol="".

Any SDK/network error on either source is logged and treated as empty
(never raises). feedparser is optional; if absent, RSS is skipped.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

import yfinance

from config import settings

from .base import NewsItem, NewsProvider

logger = logging.getLogger(__name__)


class YahooNewsProvider(NewsProvider):
    """News items from yfinance per-symbol feeds plus configured RSS feeds."""

    def get_news(self, symbols: list[str], since: datetime) -> list[NewsItem]:
        """
        Fetch news for the given symbols (yfinance) plus market-wide RSS,
        published at or after `since`.

        Args:
            symbols: ticker symbols to query via yfinance.
            since: only items with ts >= since are returned.

        Returns:
            list[NewsItem]; empty on any error (never raises).
        """
        # The provider produces tz-aware datetimes; coerce a naive `since` to UTC
        # so comparisons never raise TypeError (aware vs naive).
        if since.tzinfo is None:
            since = since.replace(tzinfo=timezone.utc)
        items: list[NewsItem] = []
        for symbol in symbols:
            items.extend(self._get_symbol_news(symbol, since))
        items.extend(self._get_rss_news(since))
        return items

    @staticmethod
    def _get_symbol_news(symbol: str, since: datetime) -> list[NewsItem]:
        """Fetch and normalize yfinance.Ticker(symbol).news for one symbol."""
        try:
            raw_items = yfinance.Ticker(symbol).news or []
        except Exception as exc:
            logger.warning("yfinance news fetch failed for %s: %s", symbol, exc)
            return []

        items: list[NewsItem] = []
        for raw in raw_items:
            item = YahooNewsProvider._parse_yfinance_item(symbol, raw)
            if item is not None and item.ts >= since:
                items.append(item)
        return items

    @staticmethod
    def _parse_yfinance_item(symbol: str, raw: dict) -> Optional[NewsItem]:
        """Normalize one yfinance news dict, handling both nested and flat shapes."""
        content = raw.get("content")
        try:
            if content is not None:
                ts = YahooNewsProvider._parse_ts(content.get("pubDate"))
                if ts is None:
                    return None
                return NewsItem(
                    symbol=symbol,
                    ts=ts,
                    source=(content.get("provider") or {}).get("displayName", ""),
                    headline=content.get("title", ""),
                    summary=content.get("summary") or "",
                    url=(content.get("canonicalUrl") or {}).get("url", ""),
                )
            epoch = raw.get("providerPublishTime")
            if epoch is None:
                return None
            ts = datetime.fromtimestamp(epoch, tz=timezone.utc)
            return NewsItem(
                symbol=symbol,
                ts=ts,
                source=raw.get("publisher", ""),
                headline=raw.get("title", ""),
                summary=raw.get("summary") or "",
                url=raw.get("link", ""),
            )
        except Exception as exc:
            logger.warning("Failed to parse yfinance news item for %s: %s", symbol, exc)
            return None

    @staticmethod
    def _parse_ts(value) -> Optional[datetime]:
        """Best-effort ISO-8601 string -> aware datetime."""
        if not value:
            return None
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None

    @staticmethod
    def _get_rss_news(since: datetime) -> list[NewsItem]:
        """Fetch and normalize configured RSS feeds. Symbol is always ''."""
        try:
            import feedparser
        except ImportError:
            logger.warning("feedparser not installed — skipping RSS news")
            return []

        items: list[NewsItem] = []
        for url in settings.RSS_FEEDS:
            try:
                feed = feedparser.parse(url)
            except Exception as exc:
                logger.warning("RSS fetch failed for %s: %s", url, exc)
                continue
            source = getattr(feed.feed, "title", "") if hasattr(feed, "feed") else ""
            for entry in getattr(feed, "entries", []):
                ts = YahooNewsProvider._parse_struct_time(getattr(entry, "published_parsed", None))
                if ts is None or ts < since:
                    continue
                items.append(
                    NewsItem(
                        symbol="",
                        ts=ts,
                        source=source,
                        headline=getattr(entry, "title", ""),
                        summary=getattr(entry, "summary", "") or "",
                        url=getattr(entry, "link", ""),
                    )
                )
        return items

    @staticmethod
    def _parse_struct_time(struct) -> Optional[datetime]:
        """Convert feedparser's time.struct_time (UTC) to an aware datetime."""
        if struct is None:
            return None
        try:
            return datetime(*struct[:6], tzinfo=timezone.utc)
        except (TypeError, ValueError):
            return None
