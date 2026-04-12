
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select email
from `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`stg_customers`
where email is null



  
  
      
    ) dbt_internal_test