WITH
    cleaned_sales AS (
        SELECT
            saleid,
            productid, --fix this to handle nulls
            productname,
            brand,
            category,
            retailerid,
            retailername,
            channel,
            COALESCE(NULLIF(location, 'NaN'), 'Unknown') AS location,
            CAST(quantity AS INT) AS quantity,
            CAST(REPLACE(price, 'USD', '') AS NUMERIC) AS price,
            CAST(date AS DATE) AS saledate,
            _etl_timestamp,
            sourcefilename
        FROM {{ source('raw__sales', 'fct_sales') }}
    )

SELECT * FROM cleaned_sales
