"""Load the card panel into SQLite in a shape SQL can actually work with.

The source arrives one row per account with six months of columns side by side
(PAY_6..PAY_0, BILL_AMT6..1, PAY_AMT6..1).  That layout is hostile to SQL: every
month-over-month question becomes a hand-written column pair.

So the loader unpivots it into a long `account_month` table, one row per account
per billing month, which is how a card book is actually stored.  Roll rates,
vintage curves and lagged comparisons then fall out of ordinary window
functions instead of twelve special cases.

Month numbering: 1 = April 2005 (oldest) ... 6 = September 2005 (newest).
The label, `default_next_month`, is observed after month 6.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "uci_default.xls"
DB = ROOT / "data" / "portfolio.db"

# source column suffix -> month index (1 = oldest)
MONTHS = {6: 1, 5: 2, 4: 3, 3: 4, 2: 5, 1: 6}
# PAY_1 does not exist in the source; the newest repayment column is PAY_0.
PAY_COL = {6: "PAY_6", 5: "PAY_5", 4: "PAY_4", 3: "PAY_3", 2: "PAY_2", 1: "PAY_0"}

SCHEMA = """
DROP TABLE IF EXISTS account;
DROP TABLE IF EXISTS account_month;

CREATE TABLE account (
    account_id      INTEGER PRIMARY KEY,
    credit_limit    REAL    NOT NULL,
    age             INTEGER NOT NULL,
    education       TEXT    NOT NULL,
    marital_status  TEXT    NOT NULL,
    default_next_month INTEGER NOT NULL CHECK (default_next_month IN (0, 1))
);

CREATE TABLE account_month (
    account_id   INTEGER NOT NULL REFERENCES account(account_id),
    month_index  INTEGER NOT NULL CHECK (month_index BETWEEN 1 AND 6),
    month_label  TEXT    NOT NULL,
    pay_status   INTEGER NOT NULL,   -- -2/-1/0 = paid or revolving, 1..9 = months past due
    bill_amount  REAL    NOT NULL,
    paid_amount  REAL    NOT NULL,
    PRIMARY KEY (account_id, month_index)
);

CREATE INDEX idx_am_month ON account_month(month_index);
CREATE INDEX idx_am_status ON account_month(pay_status);
"""

MONTH_LABEL = {1: "2005-04", 2: "2005-05", 3: "2005-06",
               4: "2005-07", 5: "2005-08", 6: "2005-09"}

EDUCATION = {1: "graduate school", 2: "university", 3: "high school"}
MARRIAGE = {1: "married", 2: "single", 3: "other"}


def build(raw: Path = RAW, db_path: Path = DB) -> Path:
    df = pd.read_excel(raw, header=1)

    accounts = pd.DataFrame({
        "account_id": df["ID"].astype(int),
        "credit_limit": df["LIMIT_BAL"].astype(float),
        "age": df["AGE"].astype(int),
        "education": df["EDUCATION"].map(EDUCATION).fillna("other"),
        "marital_status": df["MARRIAGE"].map(MARRIAGE).fillna("other"),
        "default_next_month": df["default payment next month"].astype(int),
    })

    frames = []
    for suffix, idx in MONTHS.items():
        frames.append(pd.DataFrame({
            "account_id": df["ID"].astype(int),
            "month_index": idx,
            "month_label": MONTH_LABEL[idx],
            "pay_status": df[PAY_COL[suffix]].astype(int),
            "bill_amount": df[f"BILL_AMT{suffix}"].astype(float),
            "paid_amount": df[f"PAY_AMT{suffix}"].astype(float),
        }))
    months = pd.concat(frames).sort_values(["account_id", "month_index"])

    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    con = sqlite3.connect(db_path)
    con.executescript(SCHEMA)
    accounts.to_sql("account", con, if_exists="append", index=False)
    months.to_sql("account_month", con, if_exists="append", index=False)
    con.commit()

    n_a = con.execute("SELECT COUNT(*) FROM account").fetchone()[0]
    n_m = con.execute("SELECT COUNT(*) FROM account_month").fetchone()[0]
    con.close()
    print(f"built {db_path.name}: {n_a:,} accounts, {n_m:,} account-months")
    return db_path


if __name__ == "__main__":
    build()
