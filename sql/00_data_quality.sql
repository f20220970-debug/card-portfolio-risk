-- Data quality: is the repayment-status field coded consistently across months?
--
-- Run this BEFORE anything else.  It exists because it caught something.
--
-- pay_status is documented as: -2 no usage, -1 paid in full, 0 revolving,
-- then 1..9 for the number of cycles past due.  If that coding held in every
-- month, the share of accounts in each state would move gradually.  It does
-- not: the "1 cycle past due" state is effectively absent from the first five
-- months and then appears in volume in the sixth.
--
-- The consequence is not cosmetic.  Any month-over-month analysis that treats
-- 1 and 2 as distinct states will show accounts jumping from current straight
-- to two cycles past due, which is impossible, and will read the sixth month's
-- recoding as a surge in early delinquency.
SELECT
    month_label,
    SUM(CASE WHEN pay_status = 1 THEN 1 ELSE 0 END)  AS status_1_count,
    SUM(CASE WHEN pay_status = 2 THEN 1 ELSE 0 END)  AS status_2_count,
    SUM(CASE WHEN pay_status >= 1 THEN 1 ELSE 0 END) AS any_delinquent,
    ROUND(100.0 * SUM(CASE WHEN pay_status = 1 THEN 1 ELSE 0 END)
          / NULLIF(SUM(CASE WHEN pay_status >= 1 THEN 1 ELSE 0 END), 0), 2)
        AS pct_of_delinquent_in_status_1
FROM account_month
GROUP BY month_index, month_label
ORDER BY month_index;
