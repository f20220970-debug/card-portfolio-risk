"""Tests for the database build and the SQL analyses.

A SQL repo fails differently from a Python one: the query runs, returns a
plausible table, and is wrong. So these tests check invariants that must hold
if the query means what it says -- shares summing to 100, every account present
in every month, no bucket silently dropping rows -- rather than comparing
against a previous run's output.
"""
import sqlite3
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import build_db  # noqa: E402
import run_sql   # noqa: E402

DB = ROOT / "data" / "portfolio.db"
pytestmark = pytest.mark.skipif(
    not DB.exists(), reason="portfolio.db missing -- run src/build_db.py")


@pytest.fixture(scope="module")
def con():
    c = sqlite3.connect(DB)
    yield c
    c.close()


@pytest.fixture(scope="module")
def results():
    return run_sql.run_all(quiet=True)


# --- the database itself -----------------------------------------------------

def test_every_account_has_exactly_six_months(con):
    bad = con.execute("""
        SELECT COUNT(*) FROM (
            SELECT account_id FROM account_month
            GROUP BY account_id HAVING COUNT(*) <> 6)
    """).fetchone()[0]
    assert bad == 0


def test_account_months_reconcile_to_accounts(con):
    n_a = con.execute("SELECT COUNT(*) FROM account").fetchone()[0]
    n_m = con.execute("SELECT COUNT(*) FROM account_month").fetchone()[0]
    assert n_a == 30000
    assert n_m == n_a * 6


def test_no_orphan_account_months(con):
    orphans = con.execute("""
        SELECT COUNT(*) FROM account_month am
        LEFT JOIN account a ON a.account_id = am.account_id
        WHERE a.account_id IS NULL
    """).fetchone()[0]
    assert orphans == 0


def test_month_index_maps_to_one_label(con):
    rows = con.execute("""
        SELECT month_index, COUNT(DISTINCT month_label) FROM account_month
        GROUP BY month_index
    """).fetchall()
    assert len(rows) == 6
    assert all(n == 1 for _, n in rows)


def test_newest_month_uses_pay_0_not_pay_1():
    """PAY_1 does not exist in the source; mixing it up silently shifts a month."""
    assert build_db.PAY_COL[1] == "PAY_0"
    assert build_db.MONTHS[1] == 6      # suffix 1 is the NEWEST month
    assert build_db.MONTHS[6] == 1      # suffix 6 is the OLDEST


# --- the analyses ------------------------------------------------------------

def test_roll_rate_shares_sum_to_one_hundred_per_origin(results):
    df = results["02_roll_rates"]
    for bucket, grp in df.groupby("from_bucket"):
        assert grp["pct_of_from"].sum() == pytest.approx(100.0, abs=0.05), bucket


def test_roll_rate_buckets_do_not_lose_rows(con, results):
    """Pooled transitions must equal 5 per account: six months, five steps."""
    total = results["02_roll_rates"]["n"].sum()
    n_accounts = con.execute("SELECT COUNT(*) FROM account").fetchone()[0]
    assert total == n_accounts * 5


def test_delinquency_bands_cover_the_whole_book(results):
    df = results["03_risk_by_delinquency"]
    assert df["accounts"].sum() == 30000
    assert df["pct_of_book"].sum() == pytest.approx(100.0, abs=0.05)
    assert df["pct_of_defaults"].sum() == pytest.approx(100.0, abs=0.05)


def test_default_rate_rises_with_worst_delinquency(results):
    """If this ever fails, either the bucketing or the join is wrong."""
    rates = results["03_risk_by_delinquency"].sort_values(
        "delinquency_band")["default_rate_pct"].tolist()
    assert rates == sorted(rates)


def test_utilisation_bands_cover_the_whole_book(results):
    df = results["04_utilisation_bands"]
    assert df["accounts"].sum() == 30000
    assert df["pct_of_book"].sum() == pytest.approx(100.0, abs=0.05)


def test_limit_bands_cover_book_and_defaults(results):
    df = results["05_limit_bands"]
    assert df["accounts"].sum() == 30000
    assert df["pct_of_exposure"].sum() == pytest.approx(100.0, abs=0.05)
    assert df["pct_of_defaults"].sum() == pytest.approx(100.0, abs=0.05)


def test_early_warning_covers_every_account(results):
    assert results["07_early_warning"]["accounts"].sum() == 30000


def test_any_delinquency_at_least_doubles_the_default_rate(results):
    df = results["07_early_warning"].set_index("first_delinquent_month")
    never = float(df.loc["never", "default_rate_pct"])
    ever = df.drop(index="never")["default_rate_pct"].astype(float)
    assert (ever > 2 * never).all()


def test_payment_behaviour_excludes_thin_accounts_only(con, results):
    """The behaviour query requires 3+ billed months; nothing else may drop."""
    counted = results["06_payment_behaviour"]["accounts"].sum()
    eligible = con.execute("""
        SELECT COUNT(*) FROM (
            SELECT account_id FROM account_month
            GROUP BY account_id
            HAVING SUM(CASE WHEN bill_amount > 0 THEN 1 ELSE 0 END) >= 3)
    """).fetchone()[0]
    assert counted == eligible


# --- the data-quality finding ------------------------------------------------

def test_data_quality_query_flags_the_final_month_recoding(results):
    """The defect this repo was built around. If the source is ever fixed,
    this test fails and the README's framing needs revisiting."""
    df = results["00_data_quality"].sort_values("month_label")
    first_five = df["status_1_count"].iloc[:5].sum()
    last = int(df["status_1_count"].iloc[5])
    assert first_five < 50
    assert last > 3000
    assert last > first_five * 50


def test_overview_serious_delinquency_uses_a_comparable_cut(results):
    """The 90+ series must not show the final month's coding artefact as a
    spike; it should stay within a narrow band across the window."""
    s = results["01_portfolio_overview"]["pct_90dpd_plus"].astype(float)
    assert s.max() < 3.0
    assert s.iloc[-1] < s.max() * 1.1
