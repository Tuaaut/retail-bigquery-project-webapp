
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select submitted_at
from `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`fct_submitted_orders`
where submitted_at is null



  
  
      
    ) dbt_internal_test