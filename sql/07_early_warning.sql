-- Lead time: how early does the first delinquency show up, and how much does
-- seeing it that early tell you?
--
-- The practical question behind this is when a collections or limit-management
-- action could have been taken, not merely whether the account went bad.
WITH first_delinquency AS (
    SELECT
        account_id,
        MIN(CASE WHEN pay_status >= 1 THEN month_index END) AS first_dq_month
    FROM account_month
    GROUP BY account_id
)
SELECT
    COALESCE(CAST(f.first_dq_month AS TEXT), 'never') AS first_delinquent_month,
    COUNT(*)                                          AS accounts,
    ROUND(100.0 * AVG(a.default_next_month), 2)       AS default_rate_pct,
    -- Months of warning between the first missed cycle and the label month.
    CASE WHEN f.first_dq_month IS NULL THEN NULL
         ELSE 7 - f.first_dq_month END                AS months_of_lead_time
FROM first_delinquency f
JOIN account a ON a.account_id = f.account_id
GROUP BY f.first_dq_month
ORDER BY CASE WHEN f.first_dq_month IS NULL THEN 99 ELSE f.first_dq_month END;
