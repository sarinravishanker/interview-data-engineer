WITH
    cleaned_sales AS (
        SELECT
            saleid,
            productid,
            productname,
            brand,
            category,
            retailerid,
            retailername,
            channel,
            COALESCE(location, 'Unknown') AS location,
            CAST(quantity AS INT) AS quantity,
            CAST(REPLACE(price, 'USD', '') AS NUMERIC) AS price,
            CAST(date AS DATE) AS saledate,
            _etl_timestamp,
            filename as source_file,
        FROM {{ source('raw__sales', 'fct_sales') }}
    )

SELECT * FROM cleaned_sales
