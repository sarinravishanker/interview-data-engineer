with product_sales as (
    select
        ProductID,
        ProductName,
        Brand,
        Category,
        sum(Quantity) as TotalQuantitySold,
        sum(Price * Quantity) as TotalRevenue
    from {{ ref('stg_sales') }}
    group by ProductID, ProductName, Brand, Category
)
select * from product_sales;
