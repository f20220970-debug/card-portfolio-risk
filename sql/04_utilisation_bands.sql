-- Default rate by final-month utilisation.
-- Utilisation is the standard second axis after delinquency, and on this book
-- it does something counterintuitive that the memo discusses.
WITH final AS (
    SELECT
        am.account_id,
        am.bill_amount / NULLIF(a.credit_limit, 0) AS utilisation,
        a.credit_limit,
        a.default_next_month AS defaulted
    FROM account_month am
    JOIN account a ON a.account_id = am.account_id
    WHERE am.month_index = 6
)
SELECT
    CASE
        WHEN utilisation <= 0        THEN 'a. zero or credit balance'
        WHEN utilisation <= 0.30     THEN 'b. 0-30%'
        WHEN utilisation <= 0.60     THEN 'c. 30-60%'
        WHEN utilisation <= 0.90     THEN 'd. 60-90%'
        WHEN utilisation <= 1.00     THEN 'e. 90-100%'
        ELSE                              'f. over limit'
    END                                                 AS utilisation_band,
    COUNT(*)                                            AS accounts,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2)  AS pct_of_book,
    ROUND(100.0 * AVG(defaulted), 2)                    AS default_rate_pct,
    ROUND(AVG(credit_limit), 0)                         AS avg_limit
FROM final
GROUP BY utilisation_band
ORDER BY utilisation_band;
