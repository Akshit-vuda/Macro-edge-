"""
Tests for the Alpaca market data provider (alpaca-py based).

The alpaca-py StockHistoricalDataClient is mocked, so no keys/network needed.
"""

from unittest.mock import MagicMock

import pandas as pd
import pytest

from backend.services.data_providers.base import MarketDataProvider
from backend.services.data_providers.alpaca_provider import (
    AlpacaDataProvider,
    _to_timeframe,
)


def _fake_barset() -> object:
    """Mimic an alpaca-py BarSet: an object with a MultiIndex .df."""
    idx = pd.MultiIndex.from_tuples(
        [
            ("AAPL", pd.Timestamp("2026-06-30T04:00:00Z")),
            ("AAPL", pd.Timestamp("2026-07-01T04:00:00Z")),
        ],
        names=["symbol", "timestamp"],
    )
    df = pd.DataFrame(
        {
            "open": [281.145, 293.44],
            "high": [289.9, 296.57],
            "low": [280.7, 289.195],
            "close": [289.24, 294.42],
            "volume": [1576321, 2428489],
            "trade_count": [26831, 40000],
            "vwap": [285.0, 293.0],
        },
        index=idx,
    )
    barset = MagicMock()
    barset.df = df
    return barset


def test_implements_b1_interface() -> None:
    assert issubclass(AlpacaDataProvider, MarketDataProvider)


def test_get_bars_happy_path() -> None:
    client = MagicMock()
    client.get_stock_bars.return_value = _fake_barset()
    df = AlpacaDataProvider(client=client).get_bars("AAPL", "1d", "2026-06-30", "2026-07-01")
    assert list(df.columns) == ["ts", "open", "high", "low", "close", "volume"]
    assert len(df) == 2
    assert pd.api.types.is_datetime64_any_dtype(df["ts"])
    assert df["close"].iloc[-1] == 294.42
    assert df["volume"].dtype == "int64"


def test_get_bars_no_credentials_returns_empty(monkeypatch) -> None:
    # With no ALPACA creds, client stays None -> empty, no raise.
    # Patch settings so the test is hermetic regardless of a local .env.
    from config import settings

    monkeypatch.setattr(settings, "ALPACA_API_KEY", "")
    monkeypatch.setattr(settings, "ALPACA_SECRET_KEY", "")
    provider = AlpacaDataProvider(client=None)
    assert provider.client is None
    df = provider.get_bars("AAPL", "1d", "2026-06-30", "2026-07-01")
    assert list(df.columns) == ["ts", "open", "high", "low", "close", "volume"]
    assert df.empty


def test_get_bars_error_returns_empty_no_raise() -> None:
    client = MagicMock()
    client.get_stock_bars.side_effect = RuntimeError("boom")
    df = AlpacaDataProvider(client=client).get_bars("AAPL", "1d", "2026-06-30", "2026-07-01")
    assert df.empty
    assert list(df.columns) == ["ts", "open", "high", "low", "close", "volume"]


def test_get_bars_empty_df_returns_empty() -> None:
    client = MagicMock()
    empty = MagicMock()
    empty.df = pd.DataFrame()
    client.get_stock_bars.return_value = empty
    df = AlpacaDataProvider(client=client).get_bars("AAPL", "1d", "2026-06-30", "2026-07-01")
    assert df.empty


@pytest.mark.parametrize(
    "tf,amount,unit_name",
    [("1m", 1, "Minute"), ("5m", 5, "Minute"), ("1h", 1, "Hour"), ("1d", 1, "Day")],
)
def test_timeframe_mapping(tf, amount, unit_name) -> None:
    tframe = _to_timeframe(tf)
    assert tframe.amount_value == amount
    assert tframe.unit_value.name == unit_name


def test_timeframe_defaults_to_daily() -> None:
    assert _to_timeframe("bogus").unit_value.name == "Day"
