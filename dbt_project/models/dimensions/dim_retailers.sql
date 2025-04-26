WITH
    retailers AS (
        SELECT
            retailerid,
            retailername,
            location,
            channel
        FROM {{ ref('stg_sales') }}
        GROUP BY retailerid, retailername, location, channel
    )

SELECT * FROM retailers
