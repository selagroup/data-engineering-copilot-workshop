SELECT
  *,
  DATE(txn_date) AS txn_day,
  SUM(amount_usd) AS total_usd
FROM clean_table
GROUP BY country;
