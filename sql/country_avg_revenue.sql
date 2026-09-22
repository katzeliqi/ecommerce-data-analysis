select
    Country,
    count(distinct CustomerID) as user_count,
    count(distinct InvoiceNo) as order_count,
    sum(SalesAmount) as revenue,
    round(sum(SalesAmount)/
        count(distinct InvoiceNo),2) as avg_order_value
from
    cleaned_orders
where
    is_return=0
    and country !='United Kingdom'
group by
    Country
having
    count(distinct InvoiceNo)>=10
order by
    avg_order_value desc
limit 20;
