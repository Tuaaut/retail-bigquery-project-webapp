
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select quantity
from `bq-test-query`.`analytics_dev`.`stg_order_items`
where quantity is null



  
  
      
    ) dbt_internal_test