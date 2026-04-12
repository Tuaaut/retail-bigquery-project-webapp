
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select line_amount
from `bq-test-query`.`analytics_dev`.`stg_order_items`
where line_amount is null



  
  
      
    ) dbt_internal_test