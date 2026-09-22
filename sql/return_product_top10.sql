select
    Description,
    count(distinct InvoiceNo) as return_orders,
    sum(abs(SalesAmount)) as total_return_amount
from
    cleaned_orders
where
    is_return=1
    and StockCode Regexp '^[0-9]'
    and Description is not null
group by
    Description
order by
    total_return_amount desc
limit 10;
