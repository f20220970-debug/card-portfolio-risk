-- Delinquency roll rates on a bucketing that survives the coding defect found
-- by 00_data_quality.sql.
--
-- Because "1 cycle past due" is not coded consistently across months, 1 and 2
-- are collapsed into a single "early delinquency" bucket.  That is the finest
-- split this data actually supports; a four-bucket matrix on these columns
-- produces transitions that cannot occur.
--
-- Roll rates are the leading indicator a level does not give you: a stable
-- default rate can sit on top of a book where the flow INTO delinquency has
-- doubled, and the level only catches up a quarter later.
WITH bucketed AS (
    SELECT
        account_id,
        month_index,
        CASE
            WHEN pay_status <= 0      THEN '1 current'
            WHEN pay_status BETWEEN 1 AND 2 THEN '2 early (1-2 cycles)'
            ELSE                           '3 serious (3+ cycles)'
        END AS bucket
    FROM account_month
),
transitions AS (
    SELECT
        month_index                                                      AS from_month,
        bucket                                                           AS from_bucket,
        LEAD(bucket)      OVER (PARTITION BY account_id ORDER BY month_index) AS to_bucket
    FROM bucketed
)
SELECT
    from_bucket,
    to_bucket,
    COUNT(*) AS n,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY from_bucket), 2) AS pct_of_from
FROM transitions
WHERE to_bucket IS NOT NULL
GROUP BY from_bucket, to_bucket
ORDER BY from_bucket, to_bucket;
