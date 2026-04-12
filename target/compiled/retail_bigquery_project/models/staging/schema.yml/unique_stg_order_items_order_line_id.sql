
    
    

with dbt_test__target as (

  select order_line_id as unique_field
  from `bq-test-query`.`analytics_dev`.`stg_order_items`
  where order_line_id is not null

)

select
    unique_field,
    count(*) as n_records

from dbt_test__target
group by unique_field
having count(*) > 1


