-- Default rate and exposure concentration by credit limit band.
WITH final AS (
    SELECT
        a.account_id,
        a.credit_limit,
        a.default_next_month AS defaulted,
        am.bill_amount       AS balance
    FROM account a
    JOIN account_month am
      ON am.account_id = a.account_id AND am.month_index = 6
)
SELECT
    CASE
        WHEN credit_limit <  50000  THEN 'a. under 50k'
        WHEN credit_limit < 100000  THEN 'b. 50-100k'
        WHEN credit_limit < 200000  THEN 'c. 100-200k'
        WHEN credit_limit < 400000  THEN 'd. 200-400k'
        ELSE                             'e. 400k+'
    END                                                        AS limit_band,
    COUNT(*)                                                   AS accounts,
    ROUND(100.0 * AVG(defaulted), 2)                           AS default_rate_pct,
    ROUND(SUM(balance) / 1e6, 1)                               AS exposure_m,
    ROUND(100.0 * SUM(balance) / SUM(SUM(balance)) OVER (), 2) AS pct_of_exposure,
    ROUND(100.0 * SUM(defaulted) / SUM(SUM(defaulted)) OVER (), 2) AS pct_of_defaults
FROM final
GROUP BY limit_band
ORDER BY limit_band;
