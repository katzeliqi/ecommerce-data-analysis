select
    StockCode,
    Description,
    count(distinct InvoiceNo) as order_count,
    sum(quantity) as total_qty,
    sum(SalesAmount) as total_revenue,
    count(distinct CustomerID) as buyer_count
from
    cleaned_orders
where
    is_return=0
    and Description is not null
    and StockCode regexp '^[0-9]'
group by
    StockCode,Description
order by
    total_revenue desc;