"""
Tests for the moomoo OpenD data provider + screener (B3).

The moomoo SDK / OpenD gateway is mocked, so these run without a live gateway.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pandas as pd
from moomoo import RET_OK

from backend.services.data_providers.base import MarketDataProvider, ScreenerProvider
from backend.services.data_providers.moomoo_provider import (
    MoomooDataProvider,
    MoomooScreener,
)

MODULE = "backend.services.data_providers.moomoo_provider"


def _fake_kline_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "code": ["US.AAPL", "US.AAPL"],
            "time_key": ["2026-06-30 00:00:00", "2026-07-01 00:00:00"],
            "open": [200.0, 201.0],
            "high": [205.0, 206.0],
            "low": [199.0, 200.5],
            "close": [204.0, 205.5],
            "volume": [1000000, 1100000],
            "turnover": [1.0, 1.0],
        }
    )


def test_providers_implement_b1_interfaces() -> None:
    assert issubclass(MoomooDataProvider, MarketDataProvider)
    assert issubclass(MoomooScreener, ScreenerProvider)


def test_get_bars_happy_path() -> None:
    ctx = MagicMock()
    ctx.request_history_kline.return_value = (RET_OK, _fake_kline_df(), None)
    with patch(f"{MODULE}._opend_reachable", return_value=True), patch(
        f"{MODULE}.OpenQuoteContext", return_value=ctx
    ):
        df = MoomooDataProvider().get_bars("US.AAPL", "1d", "2026-06-30", "2026-07-01")
    assert list(df.columns) == ["ts", "open", "high", "low", "close", "volume"]
    assert len(df) == 2
    assert pd.api.types.is_datetime64_any_dtype(df["ts"])
    assert df["close"].iloc[-1] == 205.5
    ctx.close.assert_called_once()


def test_get_bars_gateway_down_returns_empty_no_raise() -> None:
    with patch(f"{MODULE}._opend_reachable", return_value=False), patch(
        f"{MODULE}.OpenQuoteContext"
    ) as ctx_cls:
        df = MoomooDataProvider().get_bars("US.AAPL", "1d", "2026-06-30", "2026-07-01")
    assert list(df.columns) == ["ts", "open", "high", "low", "close", "volume"]
    assert df.empty
    ctx_cls.assert_not_called()  # never tried to open a context


def test_get_bars_request_failure_returns_empty() -> None:
    ctx = MagicMock()
    ctx.request_history_kline.return_value = (-1, "no quote permission", None)
    with patch(f"{MODULE}._opend_reachable", return_value=True), patch(
        f"{MODULE}.OpenQuoteContext", return_value=ctx
    ):
        df = MoomooDataProvider().get_bars("US.AAPL", "1d", "2026-06-30", "2026-07-01")
    assert df.empty
    ctx.close.assert_called_once()


def test_screen_happy_path_has_symbol_column() -> None:
    items = [
        SimpleNamespace(stock_code="US.AAPL", stock_name="Apple", cur_price=205.5,
                        market_val=3.1e12, pe_ttm=30.0, volume=1100000, change_rate=1.2),
        SimpleNamespace(stock_code="US.MSFT", stock_name="Microsoft", cur_price=430.0,
                        market_val=3.0e12, pe_ttm=35.0, volume=900000, change_rate=-0.4),
    ]
    ctx = MagicMock()
    ctx.get_stock_filter.return_value = (RET_OK, (True, 2, items))
    with patch(f"{MODULE}._opend_reachable", return_value=True), patch(
        f"{MODULE}.OpenQuoteContext", return_value=ctx
    ):
        df = MoomooScreener().screen({"market": "US", "min_market_cap": 1e12, "limit": 5})
    assert "symbol" in df.columns
    assert list(df["symbol"]) == ["US.AAPL", "US.MSFT"]
    assert df["price"].iloc[0] == 205.5
    ctx.close.assert_called_once()


def test_screen_gateway_down_returns_empty_no_raise() -> None:
    with patch(f"{MODULE}._opend_reachable", return_value=False), patch(
        f"{MODULE}.OpenQuoteContext"
    ) as ctx_cls:
        df = MoomooScreener().screen({"market": "US"})
    assert "symbol" in df.columns
    assert df.empty
    ctx_cls.assert_not_called()


def test_build_filters_defaults_to_one_filter() -> None:
    # empty criteria still yields a filter so get_stock_filter has something to send
    assert len(MoomooScreener._build_filters({})) == 1
    # a price range produces a filter with is_no_filter disabled
    flt = MoomooScreener._build_filters({"min_price": 10, "max_price": 100})
    assert len(flt) == 1
    assert flt[0].is_no_filter is False
