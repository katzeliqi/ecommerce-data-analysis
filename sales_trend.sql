SELECT
    DATE_FORMAT(InvoiceDate, '%%Y-%%m') AS month,
    COUNT(DISTINCT InvoiceNo) AS order_count,
    COUNT(DISTINCT CustomerID) AS active_users,
    SUM(SalesAmount) AS monthly_revenue,
    ROUND(SUM(SalesAmount) / COUNT(DISTINCT InvoiceNo), 2) AS avg_order_value
FROM
    cleaned_orders
WHERE
    is_return = 0
GROUP BY
    DATE_FORMAT(InvoiceDate, '%%Y-%%m')
ORDER BY
    month;
