
    
    

with all_values as (

    select
        order_status as value_field,
        count(*) as n_records

    from `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`stg_orders`
    group by order_status

)

select *
from all_values
where value_field not in (
    'completed','pending','cancelled'
)


