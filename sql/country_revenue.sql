select
    Country,
    count(distinct CustomerID) as user_count,
    count(distinct InvoiceNo) as order_count,
    sum(SalesAmount) as revenue,
    round(sum(SalesAmount) /
        count(distinct InvoiceNo),2) as avg_order_value
from
    cleaned_orders
where
    is_return=0
group by
    Country
order by
    revenue desc
limit 15;
