"""
DuckDB/Parquet data lake for provider bars (B4).

Stores B1-schema bar batches (ts, open, high, low, close, volume) as Parquet
under `root/bars/symbol=<SYM>/date=<YYYY-MM-DD>/` (hive partitioning) and
queries them back via DuckDB. Every incoming batch is validated with pandera;
invalid rows are quarantined to `root/quarantine/` with a logged WARNING
naming the reason, while the valid rows still get written.

On any filesystem/DB error, methods log a warning and return empty
(right-shaped) results / 0 rows written — never raise.
"""

from __future__ import annotations

import logging
from pathlib import Path
from uuid import uuid4

import duckdb
import pandas as pd
import pandera.pandas as pa
import pyarrow
import pyarrow.parquet as pq

from config import settings

logger = logging.getLogger(__name__)

_BARS_COLUMNS = ["ts", "open", "high", "low", "close", "volume"]

_BARS_SCHEMA = pa.DataFrameSchema(
    {
        "ts": pa.Column("datetime64[ns]", coerce=True),
        "open": pa.Column(float, pa.Check.gt(0), coerce=True),
        "high": pa.Column(float, pa.Check.gt(0), coerce=True),
        "low": pa.Column(float, pa.Check.gt(0), coerce=True),
        "close": pa.Column(float, pa.Check.gt(0), coerce=True),
        "volume": pa.Column("int64", pa.Check.ge(0), coerce=True),
    },
    checks=pa.Check(lambda df: df["high"] >= df["low"], name="high_ge_low"),
)


def _empty_bars() -> pd.DataFrame:
    """Empty DataFrame with the B1 bar columns."""
    return pd.DataFrame(columns=_BARS_COLUMNS)


class Lake:
    """Parquet bar lake with pandera validation and DuckDB reads."""

    def __init__(self, root: str | Path | None = None) -> None:
        """
        Args:
            root: lake root directory. Defaults to settings.DATA_DIR / 'lake'.
                Created lazily on first write.
        """
        self.root = Path(root) if root is not None else settings.DATA_DIR / "lake"

    def write_bars(self, df: pd.DataFrame, symbol: str) -> int:
        """
        Validate and write a batch of bars for a symbol.

        Valid rows go to Parquet under root/bars/symbol=<SYM>/date=<YYYY-MM-DD>/
        (date derived from ts); repeated writes for the same partition append
        new part files. Invalid rows are quarantined to root/quarantine/ with a
        logged WARNING naming the reason.

        Args:
            df: B1-schema bars (ts, open, high, low, close, volume).
            symbol: ticker symbol the bars belong to.

        Returns:
            Number of valid rows written (0 on empty/all-invalid input or any
            I/O error — never raises).
        """
        if df is None or df.empty:
            return 0
        try:
            valid, invalid, reason = self._split_valid(df)
            if not invalid.empty:
                self._quarantine(invalid, symbol, reason)
            if valid.empty:
                return 0

            data = valid.copy()
            data["symbol"] = symbol
            data["date"] = data["ts"].dt.strftime("%Y-%m-%d")
            table = pyarrow.Table.from_pandas(data, preserve_index=False)
            bars_dir = self.root / "bars"
            bars_dir.mkdir(parents=True, exist_ok=True)
            pq.write_to_dataset(
                table,
                root_path=str(bars_dir),
                partition_cols=["symbol", "date"],
                # Unique basename so same-partition writes accumulate part files.
                basename_template=f"{uuid4().hex}-{{i}}.parquet",
            )
            return len(valid)
        except Exception as exc:
            logger.warning("Lake write_bars failed for %s: %s", symbol, exc)
            return 0

    def read_bars(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        """
        Query bars for a symbol from the Parquet lake via DuckDB.

        Args:
            symbol: ticker symbol.
            start: inclusive start date "YYYY-MM-DD".
            end: inclusive end date "YYYY-MM-DD".

        Returns:
            B1-schema DataFrame sorted by ts, filtered to [start, end]
            inclusive. Missing symbol/empty lake/any error → empty DataFrame
            with the B1 columns — never raises.
        """
        try:
            bars_dir = self.root / "bars"
            if not any(bars_dir.rglob("*.parquet")):
                return _empty_bars()
            pattern = (bars_dir / "**" / "*.parquet").as_posix().replace("'", "''")
            sql = (
                "SELECT ts, open, high, low, close, volume "
                f"FROM read_parquet('{pattern}', hive_partitioning=true) "
                "WHERE symbol = ? "
                "AND CAST(date AS DATE) BETWEEN CAST(? AS DATE) AND CAST(? AS DATE) "
                "ORDER BY ts"
            )
            with duckdb.connect() as con:
                out = con.execute(sql, [symbol, start, end]).df()
            out["ts"] = pd.to_datetime(out["ts"])
            out["volume"] = out["volume"].astype("int64")
            return out[_BARS_COLUMNS]
        except Exception as exc:
            logger.warning("Lake read_bars failed for %s: %s", symbol, exc)
            return _empty_bars()

    @staticmethod
    def _split_valid(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, str]:
        """
        Lazily validate a batch against the B1 bars schema.

        Returns:
            (valid, invalid, reason): coerced valid rows, original invalid
            rows, and a short reason string naming the failed checks.
        """
        try:
            return _BARS_SCHEMA.validate(df, lazy=True), df.iloc[0:0], ""
        except pa.errors.SchemaErrors as err:
            cases = err.failure_cases
            reason = ", ".join(sorted(cases["check"].astype(str).unique()))
            bad_idx = cases["index"].dropna().unique()
            if cases["index"].isna().any() or len(bad_idx) == 0:
                # Schema-level failure (missing/uncoercible column): all bad.
                return df.iloc[0:0], df, reason
            valid = df.loc[~df.index.isin(bad_idx)]
            try:
                return _BARS_SCHEMA.validate(valid), df.loc[df.index.isin(bad_idx)], reason
            except pa.errors.SchemaError as exc:
                return df.iloc[0:0], df, f"{reason}; revalidation failed: {exc}"

    def _quarantine(self, invalid: pd.DataFrame, symbol: str, reason: str) -> None:
        """Write invalid rows to root/quarantine/ and log a WARNING with the reason."""
        qdir = self.root / "quarantine"
        qdir.mkdir(parents=True, exist_ok=True)
        path = qdir / f"{symbol}-{uuid4().hex}.parquet"
        invalid.to_parquet(path, index=False)
        logger.warning(
            "Quarantined %d invalid bar row(s) for %s to %s — failed checks: %s",
            len(invalid), symbol, path, reason,
        )
