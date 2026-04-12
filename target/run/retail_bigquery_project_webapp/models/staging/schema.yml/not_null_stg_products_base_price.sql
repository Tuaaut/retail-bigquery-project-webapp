
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select base_price
from `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`stg_products`
where base_price is null



  
  
      
    ) dbt_internal_test