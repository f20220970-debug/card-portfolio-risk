"""Build the risk-profile workbook from the SQL outputs.

python src/build_workbook.py

Conventions follow the usual financial-model colour code so a reviewer can see
at a glance what is an input and what is derived:

    blue text   - a figure that came from the data or is an assumption
    black text  - a live formula
    yellow fill - an assumption the reader is meant to change

Every derived number in this workbook is a formula referencing its inputs, not
a value pasted in from Python.  Change an assumption and the sheet moves.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT = ROOT / "model" / "card_portfolio_risk.xlsx"

FONT = "Arial"
BLUE = Font(name=FONT, size=10, color="0000FF")
BLACK = Font(name=FONT, size=10)
BOLD = Font(name=FONT, size=10, bold=True)
TITLE = Font(name=FONT, size=14, bold=True)
H2 = Font(name=FONT, size=11, bold=True)
MUTED = Font(name=FONT, size=9, italic=True, color="595959")
YELLOW = PatternFill("solid", fgColor="FFFF00")
HEADFILL = PatternFill("solid", fgColor="D9D9D9")
THIN = Side(style="thin", color="BFBFBF")
BOX = Border(bottom=THIN)

PCT = "0.00%"
PCT1 = "0.0%"
NUM = "#,##0"
MONEY = "#,##0;(#,##0);-"


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(RESULTS / f"{name}.csv")


def put(ws, row, col, value, font=BLACK, fmt=None, fill=None, align=None):
    c = ws.cell(row=row, column=col, value=value)
    c.font = font
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    if align:
        c.alignment = Alignment(horizontal=align)
    return c


def header_row(ws, row, labels, start=1):
    for i, lab in enumerate(labels):
        c = put(ws, row, start + i, lab, BOLD, fill=HEADFILL)
        c.border = BOX
        c.alignment = Alignment(horizontal="center", wrap_text=True)


def widths(ws, spec: dict[int, int]):
    for col, w in spec.items():
        ws.column_dimensions[get_column_letter(col)].width = w


# --------------------------------------------------------------------------- #

def sheet_cover(wb, overview, rollm):
    ws = wb.create_sheet("Cover")
    widths(ws, {1: 3, 2: 50, 3: 14, 4: 4, 5: 12, 6: 40})

    put(ws, 2, 2, "Card Portfolio Risk Profile", TITLE)
    put(ws, 3, 2, "Taiwan card book, April-September 2005 (UCI, Yeh & Lien 2009)", MUTED)

    put(ws, 5, 2, "Question", H2)
    put(ws, 6, 2, "What is this book's risk profile, and is it getting worse?", BLACK)

    put(ws, 8, 2, "Answer", H2)
    put(ws, 9, 2, "Deteriorating steadily, not collapsing. Across the four", BLACK)
    put(ws, 10, 2, "comparable transitions the flow into delinquency roughly", BLACK)
    put(ws, 11, 2, "doubled and cure rates held flat, against exposure growth of:", BLACK)
    put(ws, 11, 5, "=Overview!C11/Overview!C6-1", BLACK, PCT1)

    put(ws, 13, 2, "Inflow to 2+ cycles, first comparable transition", BLACK)
    put(ws, 13, 3, "='Roll rates'!E5/100", BLACK, PCT)
    put(ws, 14, 2, "Inflow to 2+ cycles, last comparable transition", BLACK)
    put(ws, 14, 3, "='Roll rates'!E8/100", BLACK, PCT)
    put(ws, 15, 2, "Deterioration multiple", BLACK)
    put(ws, 15, 3, "=C14/C13", BOLD, "0.0x")

    put(ws, 17, 2, "Cure rate, first comparable transition", BLACK)
    put(ws, 17, 3, "='Roll rates'!F5/100", BLACK, PCT)
    put(ws, 18, 2, "Cure rate, last comparable transition", BLACK)
    put(ws, 18, 3, "='Roll rates'!F8/100", BLACK, PCT)
    put(ws, 19, 2, "The fifth transition is excluded: see 'Data quality'.", MUTED)

    put(ws, 20, 2, "Colour code", H2)
    put(ws, 21, 2, "Blue text", BLUE)
    put(ws, 21, 3, "sourced figure or assumption", MUTED)
    put(ws, 22, 2, "Black text", BLACK)
    put(ws, 22, 3, "live formula", MUTED)
    put(ws, 23, 2, "Yellow fill", BLACK, fill=YELLOW)
    put(ws, 23, 3, "assumption you are meant to change", MUTED)

    put(ws, 25, 2, "Data quality warning", H2)
    put(ws, 26, 2, "The repayment-status field is not coded consistently across", BLACK)
    put(ws, 27, 2, "months: '1 cycle past due' appears 34 times across the first", BLACK)
    put(ws, 28, 2, "five months and 3,688 times in the sixth. Buckets in this", BLACK)
    put(ws, 29, 2, "workbook collapse 1 and 2 for that reason. See the", BLACK)
    put(ws, 30, 2, "'Data quality' sheet.", BLACK)

    put(ws, 32, 2, "Source", H2)
    put(ws, 33, 2, "UCI Machine Learning Repository, Default of Credit Card Clients "
                   "(30,000 accounts, 180,000 account-months).", MUTED)


def sheet_overview(wb, df):
    ws = wb.create_sheet("Overview")
    widths(ws, {1: 3, 2: 14, 3: 14, 4: 14, 5: 14, 6: 14, 7: 14, 8: 14})
    put(ws, 2, 2, "Portfolio by billing month", TITLE)
    put(ws, 3, 2, "Sourced columns in blue; growth and ratios are formulas.", MUTED)

    header_row(ws, 5, ["Month", "Exposure (000s)", "Delinquent %",
                       "90+ DPD %", "Utilisation %", "Payment rate %",
                       "Exposure growth"], start=2)
    r = 6
    for _, row in df.iterrows():
        put(ws, r, 2, row["month_label"], BLUE)
        put(ws, r, 3, float(row["exposure_m"]) * 1000, BLUE, MONEY)
        put(ws, r, 4, float(row["pct_delinquent"]) / 100, BLUE, PCT)
        put(ws, r, 5, float(row["pct_90dpd_plus"]) / 100, BLUE, PCT)
        put(ws, r, 6, float(row["utilisation_pct"]) / 100, BLUE, PCT)
        put(ws, r, 7, float(row["payment_rate_pct"]) / 100, BLUE, PCT)
        if r > 6:
            put(ws, r, 8, f"=C{r}/C{r-1}-1", BLACK, PCT)
        else:
            put(ws, r, 8, "-", MUTED, align="center")
        r += 1

    put(ws, r + 1, 2, "Growth over the window", BOLD)
    put(ws, r + 1, 3, f"=C{r-1}/C6-1", BOLD, PCT)
    put(ws, r + 3, 2, "Note: the delinquent % in the final month is inflated by a "
                      "recoding of the 1-cycle state, not by a surge in missed "
                      "payments. The 90+ DPD series is the comparable one.", MUTED)


def sheet_roll(wb, bymonth, matrix):
    ws = wb.create_sheet("Roll rates")
    widths(ws, {1: 3, 2: 16, 3: 15, 4: 15, 5: 16, 6: 16, 7: 16, 8: 14, 9: 14})
    put(ws, 2, 2, "Delinquency roll rates", TITLE)
    put(ws, 3, 2, "Transition-level flows. Percentages as sourced; multiples are formulas.", MUTED)

    header_row(ws, 4, ["Comparable?", "Inflow, any DQ %", "Cure, any DQ %",
                       "Inflow, 2+ cycles %", "Cure, 2+ cycles %",
                       "Inflow, 3+ cycles %"], start=2)
    r = 5
    for _, row in bymonth.iterrows():
        put(ws, r, 2, row["status"], BLUE)
        put(ws, r, 3, float(row["inflow_any_pct"]), BLUE, "0.00")
        put(ws, r, 4, float(row["cure_any_pct"]), BLUE, "0.00")
        put(ws, r, 5, float(row["inflow_2plus_pct"]), BLUE, "0.00")
        put(ws, r, 6, float(row["cure_2plus_pct"]), BLUE, "0.00")
        put(ws, r, 7, float(row["inflow_3plus_pct"]), BLUE, "0.00")
        r += 1

    put(ws, r + 1, 2, "Inflow multiple over comparable transitions (2+ cycles)", BOLD)
    put(ws, r + 1, 5, f"=E{r-2}/E5", BOLD, "0.0x")
    put(ws, r + 2, 2, "Inflow multiple, 3+ cycles", BOLD)
    put(ws, r + 2, 5, f"=G{r-2}/G5", BOLD, "0.0x")
    put(ws, r + 3, 2, "The final row is the September recoding, not the book: under "
                      "'any DQ' it reads as a collapse, under '2+ cycles' as an "
                      "improvement. Neither is a portfolio movement.", MUTED)

    put(ws, r + 4, 2, "Transition matrix, pooled across all months", H2)
    header_row(ws, r + 5, ["From", "To", "Accounts", "% of from"], start=2)
    rr = r + 6
    for _, row in matrix.iterrows():
        put(ws, rr, 2, row["from_bucket"], BLUE)
        put(ws, rr, 3, row["to_bucket"], BLUE)
        put(ws, rr, 4, int(row["n"]), BLUE, NUM)
        put(ws, rr, 5, float(row["pct_of_from"]) / 100, BLUE, PCT)
        rr += 1


def sheet_segments(wb, dq, util, limits, behaviour, early):
    ws = wb.create_sheet("Segments")
    widths(ws, {1: 3, 2: 26, 3: 12, 4: 13, 5: 13, 6: 14, 7: 15, 8: 15})
    put(ws, 2, 2, "Where the risk sits", TITLE)
    put(ws, 3, 2, "Rate alone does not size a problem: concentration is the other half.", MUTED)

    r = 5
    put(ws, r, 2, "By worst delinquency reached", H2); r += 1
    header_row(ws, r, ["Band", "Accounts", "% of book", "Default %",
                       "% of exposure", "% of all defaults"], start=2)
    r += 1
    first = r
    for _, row in dq.iterrows():
        put(ws, r, 2, row["delinquency_band"], BLUE)
        put(ws, r, 3, int(row["accounts"]), BLUE, NUM)
        put(ws, r, 4, float(row["pct_of_book"]) / 100, BLUE, PCT)
        put(ws, r, 5, float(row["default_rate_pct"]) / 100, BLUE, PCT)
        put(ws, r, 6, float(row["pct_of_exposure"]) / 100, BLUE, PCT)
        put(ws, r, 7, float(row["pct_of_defaults"]) / 100, BLUE, PCT)
        r += 1
    put(ws, r, 2, "Total", BOLD)
    put(ws, r, 3, f"=SUM(C{first}:C{r-1})", BOLD, NUM)
    put(ws, r, 4, f"=SUM(D{first}:D{r-1})", BOLD, PCT)
    put(ws, r, 6, f"=SUM(F{first}:F{r-1})", BOLD, PCT)
    put(ws, r, 7, f"=SUM(G{first}:G{r-1})", BOLD, PCT)
    # Account-weighted portfolio default rate, not an average of band rates.
    put(ws, r, 5, f"=SUMPRODUCT(C{first}:C{r-1},E{first}:E{r-1})/C{r}", BOLD, PCT)
    r += 2
    put(ws, r, 2, "The never-delinquent band holds this share of exposure", BLACK)
    put(ws, r, 5, f"=F{first}", BOLD, PCT)
    r += 1
    put(ws, r, 2, "and produces this share of all defaults", BLACK)
    put(ws, r, 5, f"=G{first}", BOLD, PCT)
    r += 3

    def block(title, frame, cols, labels):
        nonlocal r
        put(ws, r, 2, title, H2); r += 1
        header_row(ws, r, labels, start=2); r += 1
        for _, row in frame.iterrows():
            put(ws, r, 2, row[cols[0]], BLUE)
            for i, c in enumerate(cols[1:], start=3):
                v = float(row[c])
                put(ws, r, i, v / 100 if c.endswith("_pct") else v, BLUE,
                    PCT if c.endswith("_pct") else NUM)
            r += 1
        r += 2

    block("By final-month utilisation", util,
          ["utilisation_band", "accounts", "pct_of_book", "default_rate_pct"],
          ["Band", "Accounts", "% of book", "Default %"])
    block("By credit limit", limits,
          ["limit_band", "accounts", "default_rate_pct", "pct_of_exposure",
           "pct_of_defaults"],
          ["Band", "Accounts", "Default %", "% of exposure", "% of all defaults"])
    block("By payment behaviour", behaviour,
          ["behaviour", "accounts", "pct_of_book", "default_rate_pct"],
          ["Segment", "Accounts", "% of book", "Default %"])
    block("By month of first delinquency", early,
          ["first_delinquent_month", "accounts", "default_rate_pct"],
          ["First delinquent month", "Accounts", "Default %"])


def sheet_sensitivity(wb):
    ws = wb.create_sheet("Loss sensitivity")
    widths(ws, {1: 3, 2: 34, 3: 16, 4: 16, 5: 16, 6: 16, 7: 16})
    put(ws, 2, 2, "Expected loss, and what moves it", TITLE)
    put(ws, 3, 2, "Yellow cells are assumptions. Everything else is a formula.", MUTED)

    put(ws, 5, 2, "Exposure at the final month (000s)", BLACK)
    put(ws, 5, 3, "=Overview!C11", BLACK, MONEY)
    put(ws, 6, 2, "Observed default rate", BLACK)
    put(ws, 6, 3, "=Segments!E11", BLACK, PCT)

    put(ws, 8, 2, "Assumptions", H2)
    put(ws, 9, 2, "Loss given default", BLUE, fill=YELLOW)
    put(ws, 9, 3, 0.75, BLUE, PCT, fill=YELLOW)
    put(ws, 9, 5, "industry placeholder for unsecured card debt; "
                  "not derived from this data", MUTED)
    put(ws, 10, 2, "Exposure at default, share of balance", BLUE, fill=YELLOW)
    put(ws, 10, 3, 1.00, BLUE, PCT, fill=YELLOW)
    put(ws, 11, 2, "Portfolio default rate", BLUE, fill=YELLOW)
    put(ws, 11, 3, "=C6", BLUE, PCT, fill=YELLOW)

    put(ws, 13, 2, "Expected loss (000s)", BOLD)
    put(ws, 13, 3, "=C5*C10*C11*C9", BOLD, MONEY)
    put(ws, 14, 2, "as a share of exposure", BLACK)
    put(ws, 14, 3, "=C13/C5", BLACK, PCT)

    put(ws, 16, 2, "Expected loss across default rate and LGD (000s)", H2)
    put(ws, 17, 2, "default rate down the side, LGD across the top", MUTED)
    put(ws, 18, 3, "=C9", BLACK, PCT)
    for i, lgd in enumerate([0.55, 0.65, 0.75, 0.85, 0.95]):
        put(ws, 18, 4 + i, lgd, BLUE, PCT, fill=YELLOW)
    for j, dr in enumerate([0.15, 0.20, 0.2212, 0.25, 0.30]):
        row = 19 + j
        put(ws, row, 3, dr, BLUE, PCT, fill=YELLOW)
        for i in range(5):
            col = get_column_letter(4 + i)
            put(ws, row, 4 + i, f"=$C$5*$C$10*$C{row}*{col}$18", BLACK, MONEY)

    put(ws, 25, 2, "Reading it", H2)
    put(ws, 26, 2, "LGD is an assumption and the default rate is measured, so the "
                   "grid is wider on the axis we know least about. That is the "
                   "first thing to pin down with real recovery data.", MUTED)


def main() -> int:
    overview = load("01_portfolio_overview")
    rollm = load("02b_roll_rate_by_month")
    matrix = load("02_roll_rates")
    dq_band = load("03_risk_by_delinquency")
    util = load("04_utilisation_bands")
    limits = load("05_limit_bands")
    behaviour = load("06_payment_behaviour")
    early = load("07_early_warning")
    quality = load("00_data_quality")

    wb = Workbook()
    wb.remove(wb.active)
    sheet_cover(wb, overview, rollm)
    sheet_overview(wb, overview)
    sheet_roll(wb, rollm, matrix)
    sheet_segments(wb, dq_band, util, limits, behaviour, early)
    sheet_sensitivity(wb)

    ws = wb.create_sheet("Data quality")
    widths(ws, {1: 3, 2: 14, 3: 16, 4: 16, 5: 16, 6: 22})
    put(ws, 2, 2, "Repayment-status coding by month", TITLE)
    put(ws, 3, 2, "Why the buckets in this workbook collapse 1 and 2 cycles.", MUTED)
    header_row(ws, 5, ["Month", "Status = 1", "Status = 2", "Any delinquent",
                       "Status 1 as % of delinquent"], start=2)
    r = 6
    for _, row in quality.iterrows():
        put(ws, r, 2, row["month_label"], BLUE)
        put(ws, r, 3, int(row["status_1_count"]), BLUE, NUM)
        put(ws, r, 4, int(row["status_2_count"]), BLUE, NUM)
        put(ws, r, 5, int(row["any_delinquent"]), BLUE, NUM)
        put(ws, r, 6, f"=C{r}/E{r}", BLACK, PCT)
        r += 1
    put(ws, r + 1, 2, "Status = 1 across the first five months", BOLD)
    put(ws, r + 1, 3, f"=SUM(C6:C{r-2})", BOLD, NUM)
    put(ws, r + 2, 2, "Status = 1 in the sixth month alone", BOLD)
    put(ws, r + 2, 3, f"=C{r-1}", BOLD, NUM)
    put(ws, r + 4, 2, "A state cannot appear 100x more often in one month than in "
                      "the previous five combined unless the coding changed. Any "
                      "four-bucket roll-rate matrix on these columns shows accounts "
                      "moving from current to two cycles past due in a single step, "
                      "which cannot happen.", MUTED)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
