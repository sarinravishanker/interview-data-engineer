with cleaned_sales as (
    select
        SaleID,
        ProductID,
        ProductName,
        Brand,
        Category,
        RetailerID,
        RetailerName,
        Channel,
        coalesce(Location, 'Unknown') as Location,
        cast(Quantity as int) as Quantity,
        cast(replace(Price, 'USD', '') as numeric) as Price,
        cast(Date as date) as SaleDate,
        _etl_timestamp,
        filename
    from {{ source('raw__sales', 'fct_sales') }}
)
select * from cleaned_sales;
