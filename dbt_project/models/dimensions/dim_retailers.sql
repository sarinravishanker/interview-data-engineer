with retailers as (
    select
        RetailerID,
        RetailerName,
        Location,
        Channel
    from {{ ref('stg_sales') }}
    group by RetailerID, RetailerName, Location, Channel
)
select * from retailers
