"""
Tests for the DuckDB/Parquet bars lake (B4).

Uses tmp_path as the lake root — no network, no shared state.
"""

import logging

import pandas as pd
import pytest

from backend.services.lake import _BARS_COLUMNS, Lake


def _valid_bars() -> pd.DataFrame:
    """Three valid B1-schema bars spanning two dates."""
    return pd.DataFrame(
        {
            "ts": pd.to_datetime(
                ["2026-06-30 10:00", "2026-06-30 11:00", "2026-07-01 10:00"]
            ),
            "open": [100.0, 101.0, 102.0],
            "high": [101.0, 102.0, 103.0],
            "low": [99.0, 100.0, 101.0],
            "close": [100.5, 101.5, 102.5],
            "volume": [1000, 2000, 3000],
        }
    )


def test_round_trip_and_date_filter(tmp_path) -> None:
    lake = Lake(root=tmp_path)
    assert lake.write_bars(_valid_bars(), "AAPL") == 3

    out = lake.read_bars("AAPL", "2026-06-30", "2026-07-01")
    assert list(out.columns) == _BARS_COLUMNS
    assert len(out) == 3
    assert out["ts"].is_monotonic_increasing
    assert pd.api.types.is_datetime64_any_dtype(out["ts"])
    assert out["close"].tolist() == [100.5, 101.5, 102.5]
    assert out["volume"].tolist() == [1000, 2000, 3000]

    # Inclusive date-range filter: only the two 2026-06-30 bars.
    first_day = lake.read_bars("AAPL", "2026-06-30", "2026-06-30")
    assert len(first_day) == 2


def test_multiple_writes_accumulate(tmp_path) -> None:
    lake = Lake(root=tmp_path)
    assert lake.write_bars(_valid_bars(), "SPY") == 3
    assert lake.write_bars(_valid_bars(), "SPY") == 3
    out = lake.read_bars("SPY", "2026-06-30", "2026-07-01")
    assert len(out) == 6


def test_bad_rows_quarantined_good_rows_written(tmp_path, caplog) -> None:
    df = _valid_bars()
    df.loc[1, "close"] = -5.0  # violates close > 0
    df.loc[2, "low"] = 999.0  # violates high >= low
    lake = Lake(root=tmp_path)

    with caplog.at_level(logging.WARNING, logger="backend.services.lake"):
        written = lake.write_bars(df, "AAPL")

    assert written == 1
    qfiles = list((tmp_path / "quarantine").glob("*.parquet"))
    assert qfiles, "expected a quarantine parquet file"
    quarantined = pd.concat(pd.read_parquet(f) for f in qfiles)
    assert len(quarantined) == 2
    assert any("quarantin" in rec.message.lower() for rec in caplog.records)

    out = lake.read_bars("AAPL", "2026-06-30", "2026-07-01")
    assert len(out) == 1
    assert out["close"].iloc[0] == 100.5


def test_read_unknown_symbol_returns_empty(tmp_path) -> None:
    lake = Lake(root=tmp_path)
    out = lake.read_bars("NOPE", "2026-01-01", "2026-12-31")
    assert list(out.columns) == _BARS_COLUMNS
    assert out.empty

    # Lake with data, but a symbol that was never written.
    assert lake.write_bars(_valid_bars(), "AAPL") == 3
    out = lake.read_bars("MSFT", "2026-01-01", "2026-12-31")
    assert list(out.columns) == _BARS_COLUMNS
    assert out.empty


def test_write_empty_dataframe_returns_zero(tmp_path) -> None:
    lake = Lake(root=tmp_path)
    assert lake.write_bars(pd.DataFrame(columns=_BARS_COLUMNS), "AAPL") == 0


def test_all_invalid_batch_writes_nothing(tmp_path, caplog) -> None:
    df = _valid_bars()
    df["close"] = -1.0
    lake = Lake(root=tmp_path)
    with caplog.at_level(logging.WARNING, logger="backend.services.lake"):
        assert lake.write_bars(df, "AAPL") == 0
    assert list((tmp_path / "quarantine").glob("*.parquet"))
    out = lake.read_bars("AAPL", "2026-01-01", "2026-12-31")
    assert out.empty
