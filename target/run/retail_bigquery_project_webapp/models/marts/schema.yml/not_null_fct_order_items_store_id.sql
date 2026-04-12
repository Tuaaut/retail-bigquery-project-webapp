
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select store_id
from `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`fct_order_items`
where store_id is null



  
  
      
    ) dbt_internal_test