
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select order_line_id
from `bq-test-query`.`analytics_dev`.`stg_order_items`
where order_line_id is null



  
  
      
    ) dbt_internal_test