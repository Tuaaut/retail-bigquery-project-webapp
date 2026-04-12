
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select order_line_id
from `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`stg_order_items`
where order_line_id is null



  
  
      
    ) dbt_internal_test