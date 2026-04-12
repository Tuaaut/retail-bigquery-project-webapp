
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

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



  
  
      
    ) dbt_internal_test