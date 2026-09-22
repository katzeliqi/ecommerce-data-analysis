select
    CustomerID,
    DateDiff('2011-12-09',max(InvoiceDate)) as Recency,
    count(distinct InvoiceNo) as Frequency,
    round(sum(SalesAmount),2) as Monetary
from
    cleaned_orders
where
    is_return=0
group by
    CustomerID;
