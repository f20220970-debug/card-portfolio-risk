# Card Portfolio Risk Profile

**SQL over a real card book, answering the three questions a risk committee asks: what is the risk profile, is it getting worse, and where do the losses actually sit.** Delinquency roll rates, segment concentration, a formula-driven Excel workbook and a one-page memo.

Built for a Bread Financial Data Scientist application.

📊 **[Results](https://f20220970-debug.github.io/card-portfolio-risk/)** · [Risk memo](reports/risk_memo.md) · [Workbook](model/card_portfolio_risk.xlsx) · [SQL](sql/)

---

## The headline is a data defect

The most important finding in this repo is not about credit risk. It is that **the repayment-status field is not coded consistently across months**, and that almost every analysis of this widely-used dataset is quietly wrong because of it.

"One cycle past due" appears **34 times across the first five months and 3,688 times in the sixth**:

| Month | Apr | May | Jun | Jul | Aug | Sep |
| --- | --- | --- | --- | --- | --- | --- |
| `pay_status = 1` | 0 | 0 | 2 | 4 | 28 | **3,688** |
| `pay_status = 2` | 2,766 | 2,626 | 3,159 | 3,819 | 3,927 | 2,667 |

A state cannot appear a hundred times more often in one month than in the previous five combined unless the coding changed.

**This is not cosmetic.** On the final transition:

| Delinquency defined as | Inflow | Cure rate | Reads as |
| --- | --- | --- | --- |
| `pay_status >= 1` (natural) | **11.06%** | **10.07%** | a book in free fall |
| `pay_status >= 2` (comparable) | **3.87%** | **51.50%** | a book recovering |

Both are the recoding. Neither is the portfolio. A naive four-bucket roll-rate matrix on these columns also shows accounts moving from *current* to *two cycles past due* in a single month, which cannot happen.

I had written the free-fall version into the memo before I checked. `sql/00_data_quality.sql` now runs first, `sql/02b` reports both definitions side by side so the artefact stays visible, and a test fails if the defect ever disappears from the source.

## What the book is actually doing

Using only the comparable cut and the four comparable transitions:

- **Inflow to 2+ cycles roughly doubled**, 3.20% → 5.73% a month. Inflow to 3+ cycles **more than doubled**, 0.45% → 0.98%.
- **Cure rates held flat**, 31.6% → 30.4%. So this is an inflow problem, not a collections problem.
- **Exposure grew 31.8%** and utilisation rose from 23.2% to 30.6%.
- Eventual default rate: **22.1%**.

Deteriorating steadily. Not collapsing.

## Where the losses sit

| Worst delinquency reached | % of book | Default rate | % of exposure | % of all defaults |
| --- | --- | --- | --- | --- |
| Never delinquent | 66.4% | 11.7% | **72.5%** | **35.2%** |
| Reached 1 cycle | 5.6% | 25.0% | 0.3% | 6.4% |
| Reached 2 cycles | 24.0% | 43.6% | 24.1% | **47.2%** |
| Reached 3+ cycles | 4.0% | **62.9%** | 3.2% | 11.3% |

The never-delinquent segment has the **lowest rate in the book and produces over a third of all defaults**, because 72.5% of exposure sits inside it. A strategy aimed only at delinquent accounts addresses two thirds of the problem at most — and ignores the segment carrying almost three quarters of the balance.

Three more findings, with the reasoning in the [memo](reports/risk_memo.md):

- **Utilisation is not monotone.** Zero-balance accounts default at **24.8%**, higher than every band below 60%. A zero balance bundles dormant accounts with accounts that stopped transacting because something went wrong — so "no balance" is not "no risk", and that is exactly the kind of rule that gets written.
- **Rate and concentration disagree.** Accounts under NT$50k default at 36.1% but hold 4.3% of exposure; the 200–400k band holds 38.5% of exposure and still contributes 21.7% of defaults.
- **Any delinquency triples the risk, early.** Ever-delinquent accounts default at 36–52% against 11.7%. A first miss in the opening month carries a 52.3% rate with six months of lead time.

## Structure

The source arrives one row per account with six months of columns side by side, which is hostile to SQL. `src/build_db.py` unpivots it into a long `account_month` table — one row per account per billing month, the way a card book is actually stored — so roll rates and lagged comparisons fall out of ordinary window functions instead of twelve hand-written column pairs.

| Path | Contents |
| --- | --- |
| `sql/00_data_quality.sql` | The coding check. Runs first, because it governs everything else |
| `sql/01_portfolio_overview.sql` | Exposure, delinquency, utilisation and growth by month |
| `sql/02_roll_rates.sql` | Pooled transition matrix on a bucketing that survives the defect |
| `sql/02b_roll_rate_by_month.sql` | Inflow and cure per transition, under both definitions |
| `sql/03`–`07` | Concentration by delinquency, utilisation, limit, payment behaviour, lead time |
| `model/card_portfolio_risk.xlsx` | Six sheets, 60 live formulas, loss sensitivity grid |
| `reports/risk_memo.md` | One-page memo, answer first |
| `tests/` | 16 tests on the SQL's invariants |

CTEs and window functions throughout — `LEAD` over `PARTITION BY account_id` for transitions, `SUM(...) OVER ()` for shares of book and of exposure.

## The workbook

Six sheets: Cover, Overview, Roll rates, Segments, Loss sensitivity, Data quality. Blue text is a sourced figure, black is a live formula, yellow is an assumption you are meant to change. Every derived number is a formula referencing its inputs rather than a value pasted in from Python, so changing an assumption moves the sheet. 60 formulas, zero errors on recalculation.

The loss sensitivity grid is deliberately wider on loss-given-default than on the default rate: the default rate is measured here and LGD is an industry placeholder, so the grid is widest on the axis we know least about.

## Run it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python src/get_data.py        # ~5 MB
python src/build_db.py        # 30,000 accounts, 180,000 account-months
python src/run_sql.py         # every analysis, printed and saved to results/
python src/build_workbook.py  # the Excel model
python src/build_docs.py      # the results page
pytest                        # 16 tests
```

## Tests

Written against invariants that must hold if each query means what it says, rather than against a previous run's output: shares summing to 100 within each origin bucket, every account present in all six months, pooled transitions equalling five per account, no bucket silently dropping rows, default rate rising monotonically with worst delinquency, the behaviour query excluding only the accounts it claims to. One test asserts the data defect still exists — if the source is ever corrected, it fails and this README's framing needs revisiting.

## What this cannot tell you

Six months, one issuer, one market, 2005. **No origination date**, so nothing here separates a deteriorating book from a book whose recent vintages are worse — and that distinction decides whether the answer is collections or underwriting. No recovery data, so expected loss runs on an assumed 75% LGD that is a placeholder, not a measurement. No pricing, no bureau view. The default label is observed once, after the sixth month, so nothing is a through-the-cycle estimate. Band cuts are chosen for legibility and would need re-deriving on another book.

## Source

Yeh, I. C., & Lien, C. H. (2009). *The comparisons of data mining techniques for the predictive accuracy of probability of default of credit card clients.* Expert Systems with Applications, 36(2), 2473–2480. [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients). Amounts in NT$.
