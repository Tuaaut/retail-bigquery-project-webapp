
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select submission_id
from `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`fct_submitted_orders`
where submission_id is null



  
  
      
    ) dbt_internal_test