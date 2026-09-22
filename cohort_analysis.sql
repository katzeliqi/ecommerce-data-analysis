select
    CustomerID,
    Date_Format(InvoiceDate,'%%Y-%%m') as order_month
from
    cleaned_orders
where
    is_return=0
group by
    CustomerID,Date_Format(InvoiceDate,'%%Y-%%m');