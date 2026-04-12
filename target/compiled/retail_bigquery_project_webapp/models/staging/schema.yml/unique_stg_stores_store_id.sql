
    
    

with dbt_test__target as (

  select store_id as unique_field
  from `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`stg_stores`
  where store_id is not null

)

select
    unique_field,
    count(*) as n_records

from dbt_test__target
group by unique_field
having count(*) > 1


