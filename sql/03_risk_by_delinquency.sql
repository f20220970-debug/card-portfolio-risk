-- Default rate by the worst delinquency an account reached in the six months,
-- with each band's share of the book and of total exposure.
--
-- Concentration matters as much as rate: a 60% default band holding 1% of
-- exposure is a different problem from one holding 20%.
WITH worst AS (
    SELECT
        am.account_id,
        MAX(am.pay_status)                                      AS worst_status,
        SUM(CASE WHEN am.pay_status >= 1 THEN 1 ELSE 0 END)     AS months_delinquent,
        MAX(CASE WHEN am.month_index = 6 THEN am.bill_amount END) AS final_balance
    FROM account_month am
    GROUP BY am.account_id
),
banded AS (
    SELECT
        CASE
            WHEN w.worst_status <= 0 THEN '0 never delinquent'
            WHEN w.worst_status = 1  THEN '1 reached 1 cycle'
            WHEN w.worst_status = 2  THEN '2 reached 2 cycles'
            ELSE                          '3 reached 3+ cycles'
        END                     AS delinquency_band,
        a.default_next_month    AS defaulted,
        w.final_balance         AS balance
    FROM worst w
    JOIN account a ON a.account_id = w.account_id
)
SELECT
    delinquency_band,
    COUNT(*)                                                    AS accounts,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2)          AS pct_of_book,
    ROUND(100.0 * AVG(defaulted), 2)                            AS default_rate_pct,
    ROUND(SUM(balance) / 1e6, 1)                                AS exposure_m,
    ROUND(100.0 * SUM(balance) / SUM(SUM(balance)) OVER (), 2)  AS pct_of_exposure,
    -- Share of all defaults that sit in this band: where the losses actually are.
    ROUND(100.0 * SUM(defaulted) / SUM(SUM(defaulted)) OVER (), 2) AS pct_of_defaults
FROM banded
GROUP BY delinquency_band
ORDER BY delinquency_band;
