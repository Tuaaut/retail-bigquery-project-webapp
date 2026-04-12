
    
    

with all_values as (

    select
        payment_state as value_field,
        count(*) as n_records

    from `bq-test-query`.`analytics_dev`.`fct_orders`
    group by payment_state

)

select *
from all_values
where value_field not in (
    'fully_paid','partially_paid','unpaid'
)


