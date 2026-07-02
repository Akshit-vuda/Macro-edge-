"""
moomoo (Futu) OpenD data provider + screener — READ-ONLY.

Implements the B1 interfaces (`MarketDataProvider`, `ScreenerProvider`) over the
moomoo OpenAPI SDK talking to the local OpenD gateway. No trading happens here.

Connection host/port come from `config.settings` (MOOMOO_OPEND_HOST/PORT). If the
gateway is unreachable or a request fails, methods log a clear warning and return
an empty DataFrame (never raise), so callers degrade gracefully.
"""

from __future__ import annotations

import logging
import socket
from typing import Any, Optional

import pandas as pd
from moomoo import (
    AuType,
    KLType,
    Market,
    OpenQuoteContext,
    RET_OK,
    SimpleFilter,
    StockField,
)

from config import settings

from .base import MarketDataProvider, ScreenerProvider

logger = logging.getLogger(__name__)

# B1 get_bars timeframe string -> moomoo KLType
_TIMEFRAME_TO_KLTYPE = {
    "1m": KLType.K_1M,
    "3m": KLType.K_3M,
    "5m": KLType.K_5M,
    "15m": KLType.K_15M,
    "30m": KLType.K_30M,
    "60m": KLType.K_60M,
    "1d": KLType.K_DAY,
    "1w": KLType.K_WEEK,
    "1M": KLType.K_MON,
}

_MARKET_MAP = {
    "US": Market.US,
    "HK": Market.HK,
    "SH": Market.SH,
    "SZ": Market.SZ,
    "SG": Market.SG,
    "MY": Market.MY,
    "JP": Market.JP,
}

_BARS_COLUMNS = ["ts", "open", "high", "low", "close", "volume"]
_SCREEN_COLUMNS = ["symbol", "name", "price", "market_val", "pe", "volume", "change_rate"]


def _opend_reachable(host: str, port: int, timeout: float = 2.0) -> bool:
    """Return True if a TCP connection to the OpenD gateway succeeds."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def _f(val: Any) -> float:
    """Best-effort float, 0.0 on failure/None."""
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def _i(val: Any) -> int:
    """Best-effort int, 0 on failure/None."""
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0


class _MoomooBase:
    """Shared connection config for moomoo providers."""

    def __init__(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Args:
            host: OpenD host; defaults to settings.MOOMOO_OPEND_HOST.
            port: OpenD port; defaults to settings.MOOMOO_OPEND_PORT.
        """
        self.host: str = host or settings.MOOMOO_OPEND_HOST
        self.port: int = int(port if port is not None else settings.MOOMOO_OPEND_PORT)

    def _connect(self) -> Optional[OpenQuoteContext]:
        """Open a quote context, or None (logged) if OpenD is unreachable."""
        if not _opend_reachable(self.host, self.port):
            logger.warning(
                "moomoo OpenD not reachable at %s:%s — is the gateway running and logged in?",
                self.host,
                self.port,
            )
            return None
        return OpenQuoteContext(host=self.host, port=self.port)


class MoomooDataProvider(_MoomooBase, MarketDataProvider):
    """Historical OHLCV bars from moomoo OpenD."""

    def get_bars(self, symbol: str, timeframe: str, start: str, end: str) -> pd.DataFrame:
        """
        Fetch historical bars for a moomoo-style code (e.g. "US.AAPL", "HK.00700").

        Args:
            symbol: moomoo security code, MARKET.CODE format.
            timeframe: one of 1m/3m/5m/15m/30m/60m/1d/1w/1M (defaults to daily).
            start: inclusive start date "YYYY-MM-DD".
            end: inclusive end date "YYYY-MM-DD".

        Returns:
            DataFrame with columns ts, open, high, low, close, volume
            (empty on unreachable gateway or request failure).
        """
        ktype = _TIMEFRAME_TO_KLTYPE.get(timeframe, KLType.K_DAY)
        ctx = self._connect()
        if ctx is None:
            return pd.DataFrame(columns=_BARS_COLUMNS)
        try:
            frames = []
            ret, data, page_req_key = ctx.request_history_kline(
                symbol, start=start, end=end, ktype=ktype, autype=AuType.QFQ, max_count=1000
            )
            if ret != RET_OK:
                logger.warning("moomoo request_history_kline failed for %s: %s", symbol, data)
                return pd.DataFrame(columns=_BARS_COLUMNS)
            frames.append(data)
            while page_req_key is not None:
                ret, data, page_req_key = ctx.request_history_kline(
                    symbol, start=start, end=end, ktype=ktype, autype=AuType.QFQ,
                    max_count=1000, page_req_key=page_req_key,
                )
                if ret != RET_OK:
                    logger.warning("moomoo kline pagination failed for %s: %s", symbol, data)
                    break
                frames.append(data)
            raw = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
            return self._normalize_bars(raw)
        finally:
            ctx.close()

    @staticmethod
    def _normalize_bars(raw: pd.DataFrame) -> pd.DataFrame:
        """Map moomoo kline columns to the B1 schema."""
        if raw is None or raw.empty:
            return pd.DataFrame(columns=_BARS_COLUMNS)
        out = pd.DataFrame(
            {
                "ts": pd.to_datetime(raw["time_key"]),
                "open": raw["open"].astype(float),
                "high": raw["high"].astype(float),
                "low": raw["low"].astype(float),
                "close": raw["close"].astype(float),
                "volume": raw["volume"].astype("int64"),
            }
        )
        return out[_BARS_COLUMNS]


class MoomooScreener(_MoomooBase, ScreenerProvider):
    """Stock screening via moomoo OpenD get_stock_filter."""

    def screen(self, criteria: dict) -> pd.DataFrame:
        """
        Screen stocks by criteria.

        Args:
            criteria: dict; recognized keys — market ("US"/"HK"/...), limit (int),
                min_price, max_price, min_market_cap, max_market_cap (in absolute
                currency), min_pe, max_pe, min_volume. Unknown keys are ignored.

        Returns:
            DataFrame with columns including 'symbol' (empty on unreachable gateway
            or request failure).
        """
        market = _MARKET_MAP.get(str(criteria.get("market", "US")).upper(), Market.US)
        limit = int(criteria.get("limit", 200))
        filter_list = self._build_filters(criteria)

        ctx = self._connect()
        if ctx is None:
            return pd.DataFrame(columns=_SCREEN_COLUMNS)
        try:
            ret, data = ctx.get_stock_filter(market, filter_list, begin=0, num=limit)
            if ret != RET_OK:
                logger.warning("moomoo get_stock_filter failed: %s", data)
                return pd.DataFrame(columns=_SCREEN_COLUMNS)
            # data is (last_page, all_count, stock_list)
            _last_page, _all_count, stock_list = data
            # ponytail: moomoo's FilterStockData carries symbol + filtered fields
            # (e.g. market_val) but leaves price/pe/volume at 0 unless enriched via
            # get_market_snapshot. Add that enrichment here if a consumer needs the
            # extra columns populated (requires quote entitlements).
            rows = [
                {
                    "symbol": getattr(item, "stock_code", ""),
                    "name": getattr(item, "stock_name", ""),
                    "price": _f(getattr(item, "cur_price", None)),
                    "market_val": _f(getattr(item, "market_val", None)),
                    "pe": _f(getattr(item, "pe_ttm", None)),
                    "volume": _i(getattr(item, "volume", None)),
                    "change_rate": _f(getattr(item, "change_rate", None)),
                }
                for item in stock_list
            ]
            return pd.DataFrame(rows, columns=_SCREEN_COLUMNS)
        finally:
            ctx.close()

    @staticmethod
    def _build_filters(criteria: dict) -> list:
        """Translate the criteria dict into moomoo SimpleFilter objects.

        Always returns at least one filter (market-cap sort) so get_stock_filter
        has something to serialize.
        """
        filter_list: list = []

        def _range_filter(field, lo_key, hi_key):
            lo, hi = criteria.get(lo_key), criteria.get(hi_key)
            if lo is None and hi is None:
                return
            sf = SimpleFilter()
            sf.stock_field = field
            sf.is_no_filter = False  # required, else SDK drops filter_min/max
            if lo is not None:
                sf.filter_min = lo
            if hi is not None:
                sf.filter_max = hi
            filter_list.append(sf)

        _range_filter(StockField.CUR_PRICE, "min_price", "max_price")
        _range_filter(StockField.MARKET_VAL, "min_market_cap", "max_market_cap")
        _range_filter(StockField.PE_TTM, "min_pe", "max_pe")
        if criteria.get("min_volume") is not None:
            sf = SimpleFilter()
            sf.stock_field = StockField.VOLUME
            sf.is_no_filter = False
            sf.filter_min = criteria["min_volume"]
            filter_list.append(sf)

        if not filter_list:
            sf = SimpleFilter()
            sf.stock_field = StockField.MARKET_VAL
            sf.is_no_filter = False
            sf.filter_min = 1
            filter_list.append(sf)
        return filter_list
