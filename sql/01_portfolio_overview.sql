-- Portfolio overview by billing month.
-- The question a risk committee asks first: is the book growing, and is it
-- getting worse?  Exposure, delinquency incidence and utilisation per month.
--
-- Read pct_delinquent with 00_data_quality.sql open: the sixth month's figure
-- is inflated by a recoding of the 1-cycle state, not by a surge in missed
-- payments.  pct_90dpd_plus is the comparable series across all six months.
WITH monthly AS (
    SELECT
        am.month_index,
        am.month_label,
        COUNT(*)                                            AS accounts,
        SUM(am.bill_amount)                                 AS total_exposure,
        SUM(am.paid_amount)                                 AS total_paid,
        SUM(CASE WHEN am.pay_status >= 1 THEN 1 ELSE 0 END) AS delinquent_accounts,
        -- 3+ cycles, not 2+: see 00_data_quality.sql.  The 1-vs-2 split is not
        -- coded consistently across months, so only a 3+ cut is comparable.
        SUM(CASE WHEN am.pay_status >= 3 THEN 1 ELSE 0 END) AS seriously_delinquent,
        SUM(a.credit_limit)                                 AS total_limit
    FROM account_month am
    JOIN account a ON a.account_id = am.account_id
    GROUP BY am.month_index, am.month_label
)
SELECT
    month_label,
    accounts,
    ROUND(total_exposure / 1e6, 1)                               AS exposure_m,
    ROUND(100.0 * delinquent_accounts / accounts, 2)             AS pct_delinquent,
    ROUND(100.0 * seriously_delinquent / accounts, 2)            AS pct_90dpd_plus,
    ROUND(100.0 * total_exposure / total_limit, 2)               AS utilisation_pct,
    ROUND(100.0 * total_paid / NULLIF(total_exposure, 0), 2)     AS payment_rate_pct,
    -- Month-over-month exposure growth, from the window rather than a self-join.
    ROUND(100.0 * (total_exposure - LAG(total_exposure) OVER (ORDER BY month_index))
          / NULLIF(LAG(total_exposure) OVER (ORDER BY month_index), 0), 2) AS exposure_growth_pct
FROM monthly
ORDER BY month_index;
