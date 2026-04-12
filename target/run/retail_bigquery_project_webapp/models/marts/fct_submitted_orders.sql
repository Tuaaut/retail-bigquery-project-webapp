-- back compat for old kwarg name
  
  
        
            
	    
	    
            
        
    

    

    merge into `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`fct_submitted_orders` as DBT_INTERNAL_DEST
        using (
        select
        * from `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`fct_submitted_orders__dbt_tmp`
        ) as DBT_INTERNAL_SOURCE
        on ((DBT_INTERNAL_SOURCE.order_id = DBT_INTERNAL_DEST.order_id))

    
    when matched then update set
        `submission_id` = DBT_INTERNAL_SOURCE.`submission_id`,`submitted_at` = DBT_INTERNAL_SOURCE.`submitted_at`,`order_id` = DBT_INTERNAL_SOURCE.`order_id`,`customer_id` = DBT_INTERNAL_SOURCE.`customer_id`,`store_id` = DBT_INTERNAL_SOURCE.`store_id`,`order_date` = DBT_INTERNAL_SOURCE.`order_date`,`order_amount` = DBT_INTERNAL_SOURCE.`order_amount`,`order_status` = DBT_INTERNAL_SOURCE.`order_status`
    

    when not matched then insert
        (`submission_id`, `submitted_at`, `order_id`, `customer_id`, `store_id`, `order_date`, `order_amount`, `order_status`)
    values
        (`submission_id`, `submitted_at`, `order_id`, `customer_id`, `store_id`, `order_date`, `order_amount`, `order_status`)


    