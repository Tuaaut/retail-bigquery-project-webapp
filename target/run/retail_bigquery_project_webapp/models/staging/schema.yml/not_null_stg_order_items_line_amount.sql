
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select line_amount
from `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`stg_order_items`
where line_amount is null



  
  
      
    ) dbt_internal_test