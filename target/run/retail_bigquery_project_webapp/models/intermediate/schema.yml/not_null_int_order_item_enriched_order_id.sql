
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select order_id
from `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`int_order_item_enriched`
where order_id is null



  
  
      
    ) dbt_internal_test