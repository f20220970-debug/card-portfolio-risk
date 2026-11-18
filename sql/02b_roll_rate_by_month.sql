-- Roll rates month by month, computed under two definitions of "delinquent".
--
-- This query exists in this shape because the single-definition version misled
-- me. Under the natural definition (pay_status >= 1) the final transition shows
-- the flow into delinquency tripling and the cure rate collapsing -- a book in
-- free fall. Under pay_status >= 2, which is the only cut coded consistently
-- across all six months (see 00_data_quality.sql), that same transition shows
-- inflow FALLING and the cure rate roughly doubling.
--
-- The dramatic reading was the September recoding of the 1-cycle state, not the
-- portfolio. Both columns are reported so the artefact is visible rather than
-- hidden behind whichever definition was chosen.
--
-- Read the ">= 2" column. Read transitions 1-4 only; transition 5 is not
-- comparable under either definition.
WITH b AS (
    SELECT
        account_id,
        month_index,
        CASE WHEN pay_status >= 1 THEN 1 ELSE 0 END AS dq_any,
        CASE WHEN pay_status >= 2 THEN 1 ELSE 0 END AS dq_2plus,
        CASE WHEN pay_status >= 3 THEN 1 ELSE 0 END AS dq_3plus
    FROM account_month
),
t AS (
    SELECT
        month_index AS from_month,
        dq_any, dq_2plus, dq_3plus,
        LEAD(dq_any)   OVER (PARTITION BY account_id ORDER BY month_index) AS to_any,
        LEAD(dq_2plus) OVER (PARTITION BY account_id ORDER BY month_index) AS to_2plus,
        LEAD(dq_3plus) OVER (PARTITION BY account_id ORDER BY month_index) AS to_3plus
    FROM b
)
SELECT
    from_month,
    CASE WHEN from_month = 5 THEN 'not comparable' ELSE 'comparable' END AS status,

    ROUND(100.0 * SUM(CASE WHEN dq_any = 0 AND to_any = 1 THEN 1 ELSE 0 END)
          / NULLIF(SUM(CASE WHEN dq_any = 0 THEN 1 ELSE 0 END), 0), 2)
        AS inflow_any_pct,
    ROUND(100.0 * SUM(CASE WHEN dq_any = 1 AND to_any = 0 THEN 1 ELSE 0 END)
          / NULLIF(SUM(CASE WHEN dq_any = 1 THEN 1 ELSE 0 END), 0), 2)
        AS cure_any_pct,

    ROUND(100.0 * SUM(CASE WHEN dq_2plus = 0 AND to_2plus = 1 THEN 1 ELSE 0 END)
          / NULLIF(SUM(CASE WHEN dq_2plus = 0 THEN 1 ELSE 0 END), 0), 2)
        AS inflow_2plus_pct,
    ROUND(100.0 * SUM(CASE WHEN dq_2plus = 1 AND to_2plus = 0 THEN 1 ELSE 0 END)
          / NULLIF(SUM(CASE WHEN dq_2plus = 1 THEN 1 ELSE 0 END), 0), 2)
        AS cure_2plus_pct,

    ROUND(100.0 * SUM(CASE WHEN dq_3plus = 0 AND to_3plus = 1 THEN 1 ELSE 0 END)
          / NULLIF(SUM(CASE WHEN dq_3plus = 0 THEN 1 ELSE 0 END), 0), 2)
        AS inflow_3plus_pct
FROM t
WHERE to_any IS NOT NULL
GROUP BY from_month
ORDER BY from_month;
