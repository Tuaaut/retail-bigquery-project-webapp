-- back compat for old kwarg name
  
  
        
            
	    
	    
            
        
    

    

    merge into `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`fct_order_items` as DBT_INTERNAL_DEST
        using (

-- Build the item-level fact table and only reprocess recent order dates on incremental runs.
with item_scope as (
  select *
  from `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`int_order_item_enriched`

  
    -- Re-read the latest loaded order date so merge can update late-arriving order lines safely.
    where order_date >= (select coalesce(max(order_date), date('1900-01-01')) from `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`fct_order_items`)
  
)

select
  i.order_line_id,
  i.order_id,
  i.customer_id,
  i.store_id,
  i.product_id,
  i.order_date,
  i.order_status,
  c.customer_name,
  c.city as customer_city,
  s.store_name,
  s.city as store_city,
  s.region as store_region,
  p.product_name,
  p.category,
  p.brand,
  i.quantity,
  i.unit_price,
  i.line_amount
from item_scope i
left join `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`stg_customers` c
  on i.customer_id = c.customer_id
left join `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`stg_stores` s
  on i.store_id = s.store_id
left join `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`stg_products` p
  on i.product_id = p.product_id
        ) as DBT_INTERNAL_SOURCE
        on ((DBT_INTERNAL_SOURCE.order_line_id = DBT_INTERNAL_DEST.order_line_id))

    
    when matched then update set
        `order_line_id` = DBT_INTERNAL_SOURCE.`order_line_id`,`order_id` = DBT_INTERNAL_SOURCE.`order_id`,`customer_id` = DBT_INTERNAL_SOURCE.`customer_id`,`store_id` = DBT_INTERNAL_SOURCE.`store_id`,`product_id` = DBT_INTERNAL_SOURCE.`product_id`,`order_date` = DBT_INTERNAL_SOURCE.`order_date`,`order_status` = DBT_INTERNAL_SOURCE.`order_status`,`customer_name` = DBT_INTERNAL_SOURCE.`customer_name`,`customer_city` = DBT_INTERNAL_SOURCE.`customer_city`,`store_name` = DBT_INTERNAL_SOURCE.`store_name`,`store_city` = DBT_INTERNAL_SOURCE.`store_city`,`store_region` = DBT_INTERNAL_SOURCE.`store_region`,`product_name` = DBT_INTERNAL_SOURCE.`product_name`,`category` = DBT_INTERNAL_SOURCE.`category`,`brand` = DBT_INTERNAL_SOURCE.`brand`,`quantity` = DBT_INTERNAL_SOURCE.`quantity`,`unit_price` = DBT_INTERNAL_SOURCE.`unit_price`,`line_amount` = DBT_INTERNAL_SOURCE.`line_amount`
    

    when not matched then insert
        (`order_line_id`, `order_id`, `customer_id`, `store_id`, `product_id`, `order_date`, `order_status`, `customer_name`, `customer_city`, `store_name`, `store_city`, `store_region`, `product_name`, `category`, `brand`, `quantity`, `unit_price`, `line_amount`)
    values
        (`order_line_id`, `order_id`, `customer_id`, `store_id`, `product_id`, `order_date`, `order_status`, `customer_name`, `customer_city`, `store_name`, `store_city`, `store_region`, `product_name`, `category`, `brand`, `quantity`, `unit_price`, `line_amount`)


    