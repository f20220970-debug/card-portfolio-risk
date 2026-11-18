# Card portfolio risk profile — April to September 2005

**To:** Risk committee
**Subject:** What this book's risk profile is, whether it is deteriorating, and where the losses actually sit
**Data:** 30,000 accounts, 180,000 account-months, NT$ (UCI *Default of Credit Card Clients*)

---

## Answer first

The book is **deteriorating steadily, not collapsing**. Across the four transitions that can be compared, the flow of current accounts into two-or-more cycles past due **roughly doubled, from 3.20% to 5.73%** a month, and the flow into three-or-more cycles **more than doubled, 0.45% to 0.98%**. Cure rates held roughly flat (31.6% to 30.4%), so this is an inflow problem, not a collections problem.

Meanwhile exposure grew **31.8%** over six months and utilisation rose from **23.2% to 30.6%**. The book is taking on balance faster than it is taking on accounts, and the accounts it already has are going bad at an accelerating rate.

Eventual default rate on the book: **22.1%**.

## Read the fifth transition as nothing at all

Before any of the above, one finding governs how every other number here may be used.

The repayment-status field is **not coded consistently across months**. "One cycle past due" appears **34 times across the first five months and 3,688 times in the sixth**:

| Month | Apr | May | Jun | Jul | Aug | Sep |
| --- | --- | --- | --- | --- | --- | --- |
| Status = 1 | 0 | 0 | 2 | 4 | 28 | **3,688** |
| Status = 2 | 2,766 | 2,626 | 3,159 | 3,819 | 3,927 | 2,667 |

A state cannot appear a hundred times more often in one month than in the previous five combined unless the coding changed.

This is not academic. Under the natural definition of delinquency, the final transition shows the flow into delinquency **tripling to 11.06%** while the cure rate **collapses to 10.07%** — a book in free fall. Under the comparable definition it shows inflow **falling to 3.87%** and the cure rate **rising to 51.50%** — a book recovering. Both are the recoding. Neither is the portfolio.

I had written the first version into this memo before checking. Every figure above therefore uses the two-or-more-cycles cut, and excludes the fifth transition.

## Where the losses sit

Rate and concentration are different questions, and the answer differs depending on which you ask.

| Worst delinquency reached | % of book | Default rate | % of exposure | % of all defaults |
| --- | --- | --- | --- | --- |
| Never delinquent | 66.4% | 11.7% | **72.5%** | **35.2%** |
| Reached 1 cycle | 5.6% | 25.0% | 0.3% | 6.4% |
| Reached 2 cycles | 24.0% | 43.6% | 24.1% | **47.2%** |
| Reached 3+ cycles | 4.0% | **62.9%** | 3.2% | 11.3% |

**The never-delinquent segment produces over a third of all defaults.** It has the lowest rate in the book and the highest count, and 72.5% of exposure sits inside it. A strategy built only on delinquent accounts addresses, at most, two thirds of the problem — and the segment it ignores is the one carrying almost three quarters of the balance.

The 3+ cycle band is the opposite shape: the worst rate in the book, and only 3.2% of exposure. It is a collections problem, not a capital problem.

## Four things worth acting on

**1. Any delinquency at all triples the risk, and the first one arrives early.**

An account that was ever delinquent defaults at 36–52% against **11.7%** for one that never was. Accounts first missing in the opening month default at **52.3%** — with six months of warning. Even a first miss in the final month carries a **36.1%** rate. The signal is early and it is strong; what is missing is the action attached to it.

**2. Utilisation is not monotone, and the exception is the interesting part.**

| Utilisation | Default rate | Average limit |
| --- | --- | --- |
| Zero or credit balance | **24.8%** | 209,784 |
| 0–30% | 16.9% | 216,463 |
| 30–60% | 23.2% | 144,717 |
| 60–90% | 27.6% | 117,031 |
| 90–100% | 24.3% | 106,232 |
| Over limit | **30.1%** | 109,141 |

Default rate climbs with utilisation as expected — except that **zero-balance accounts default at 24.8%, higher than any band up to 60%**. A zero balance is not evidence of health. It bundles genuinely dormant accounts with accounts that have stopped transacting because something has gone wrong. Treating "no balance" as "no risk" in a limit-management rule would be a mistake, and it is the kind of rule that gets written.

**3. Limit is inversely related to risk, but exposure is not.**

Accounts under NT$50k default at **36.1%**, against **12.0%** for those above NT$400k. But the under-50k band holds only **4.3%** of exposure, while the 200–400k band holds **38.5%** and still contributes **21.7%** of defaults. The highest-rate segment is not where the money is.

**4. Half the book is minimum payers.**

| Behaviour | % of book | Default rate | Avg 6-month billings |
| --- | --- | --- | --- |
| Transactor (pays in full) | 1.7% | 17.9% | 21,455 |
| Heavy payer | 29.2% | 14.3% | 75,463 |
| Light payer | 17.6% | 19.7% | 243,319 |
| **Minimum payer** | **51.6%** | **26.8%** | **445,467** |

Minimum payers are the majority of the book, carry the largest balances and default at nearly twice the rate of heavy payers. On a card book that is the revenue engine and the loss engine at the same time, and the two cannot be separated by tightening one lever.

*Covers 27,321 of 30,000 accounts; the rest had fewer than three months with a positive balance and are excluded rather than classified on thin evidence.*

## What I would check next

1. **Recovery data.** Expected loss here runs on an assumed 75% loss given default, which is a placeholder, not a measurement. The sensitivity grid in the workbook is wider on that axis than on the default rate for exactly that reason.
2. **Whether the September recoding is a reporting change or a policy change.** If the bank changed when an account is flagged one cycle down, that changes what every historical model was trained on.
3. **The zero-balance segment, split into dormant and distressed.** It is 8.7% of accounts at a 24.8% default rate, and the two populations inside it need opposite treatment.
4. **Vintage.** This panel has no origination date, so none of the above separates a deteriorating book from a book whose recent vintages are worse. That distinction decides whether the answer is collections or underwriting.

## What this cannot tell you

Six months, one market, one issuer, 2005. There is no origination date, no recovery data, no pricing and no credit-bureau view. The default label is observed once, after the sixth month, so nothing here is a through-the-cycle estimate. Thresholds and band cuts are chosen for legibility and would need re-deriving on another book.
