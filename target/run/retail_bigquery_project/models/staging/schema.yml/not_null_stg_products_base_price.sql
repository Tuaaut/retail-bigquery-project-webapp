
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select base_price
from `bq-test-query`.`analytics_dev`.`stg_products`
where base_price is null



  
  
      
    ) dbt_internal_test