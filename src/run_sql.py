"""Run every analysis in sql/ against the SQLite book and save each result.

python src/run_sql.py          run all, write results/*.csv
python src/run_sql.py 02       run one by its numeric prefix
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "portfolio.db"
SQL_DIR = ROOT / "sql"
RESULTS = ROOT / "results"


def run_one(con: sqlite3.Connection, path: Path) -> pd.DataFrame:
    return pd.read_sql_query(path.read_text(), con)


def run_all(prefix: str | None = None, quiet: bool = False) -> dict[str, pd.DataFrame]:
    if not DB.exists():
        raise SystemExit("portfolio.db is missing -- run python src/build_db.py first")
    RESULTS.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    out = {}
    for path in sorted(SQL_DIR.glob("*.sql")):
        if prefix and not path.name.startswith(prefix):
            continue
        name = path.stem
        df = run_one(con, path)
        df.to_csv(RESULTS / f"{name}.csv", index=False)
        out[name] = df
        if not quiet:
            print(f"\n=== {name} ===")
            print(df.to_string(index=False))
    con.close()
    return out


if __name__ == "__main__":
    run_all(sys.argv[1] if len(sys.argv) > 1 else None)
