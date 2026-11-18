-- Revolvers against transactors, by how much of the bill each account pays.
--
-- On a card book this is a behaviour segmentation, not a risk score, and the
-- two are often confused: a revolver is a profitable customer right up until
-- they are a loss.
WITH ratios AS (
    SELECT
        am.account_id,
        AVG(CASE WHEN am.bill_amount > 0
                 THEN MIN(1.0, am.paid_amount / am.bill_amount) END) AS avg_payment_ratio,
        SUM(am.bill_amount) AS total_billed
    FROM account_month am
    GROUP BY am.account_id
    HAVING SUM(CASE WHEN am.bill_amount > 0 THEN 1 ELSE 0 END) >= 3
)
SELECT
    CASE
        WHEN avg_payment_ratio IS NULL   THEN 'e. inactive'
        WHEN avg_payment_ratio >= 0.90   THEN 'a. transactor (pays in full)'
        WHEN avg_payment_ratio >= 0.30   THEN 'b. heavy payer'
        WHEN avg_payment_ratio >= 0.10   THEN 'c. light payer'
        ELSE                                  'd. minimum payer'
    END                                                 AS behaviour,
    COUNT(*)                                            AS accounts,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2)  AS pct_of_book,
    ROUND(100.0 * AVG(a.default_next_month), 2)         AS default_rate_pct,
    ROUND(AVG(r.total_billed), 0)                       AS avg_six_month_billings
FROM ratios r
JOIN account a ON a.account_id = r.account_id
GROUP BY behaviour
ORDER BY behaviour;
