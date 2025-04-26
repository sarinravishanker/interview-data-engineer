WITH
    product_sales AS (
        SELECT
            productid,
            productname,
            brand,
            category
        FROM {{ ref('stg_sales') }}
        GROUP BY productid, productname, brand, category
    )

SELECT * FROM product_sales
