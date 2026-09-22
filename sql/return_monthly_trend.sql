select
    DATE_FORMAT(InvoiceDate,'%%Y-%%m') as month,
    count(distinct InvoiceNo) as return_orders,
    sum(abs(SalesAmount)) as total_return_amount
from
    cleaned_orders
where
    is_return=1
group by
    DATE_FORMAT(InvoiceDate,'%%Y-%%m')
order by
    month;
