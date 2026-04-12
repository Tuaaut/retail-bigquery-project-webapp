
    
    

with child as (
    select store_id as from_field
    from `bq-test-query`.`analytics_dev`.`stg_orders`
    where store_id is not null
),

parent as (
    select store_id as to_field
    from `bq-test-query`.`analytics_dev`.`stg_stores`
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


