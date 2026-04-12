-- back compat for old kwarg name
  
  
        
            
	    
	    
            
        
    

    

    merge into `bq-test-query`.`analytics_dev`.`fct_orders` as DBT_INTERNAL_DEST
        using (

-- Build the order-level fact table and only reprocess recent order dates on incremental runs.
with order_scope as (
  select *
  from `bq-test-query`.`analytics_dev`.`int_orders_enriched`

  
    -- Re-read the latest loaded order date so merge can update late-arriving changes safely.
    where order_date >= (select coalesce(max(order_date), date('1900-01-01')) from `bq-test-query`.`analytics_dev`.`fct_orders`)
  
)

select
  o.order_id,
  o.customer_id,
  o.store_id,
  o.customer_name,
  o.customer_city,
  o.store_name,
  o.store_city,
  o.store_region,
  o.store_type,
  o.order_date,
  o.order_amount,
  o.order_status,
  coalesce(r.total_quantity, 0) as total_quantity,
  coalesce(r.distinct_products, 0) as distinct_products,
  coalesce(r.item_subtotal, 0) as item_subtotal,
  coalesce(p.total_paid_amount, 0) as total_paid_amount,
  coalesce(p.successful_payment_count, 0) as successful_payment_count,
  p.latest_payment_date,
  case
    when coalesce(p.total_paid_amount, 0) >= o.order_amount then 'fully_paid'
    when coalesce(p.total_paid_amount, 0) > 0 then 'partially_paid'
    else 'unpaid'
  end as payment_state
from order_scope o
left join `bq-test-query`.`analytics_dev`.`int_order_item_rollup` r
  on o.order_id = r.order_id
left join `bq-test-query`.`analytics_dev`.`int_order_payments` p
  on o.order_id = p.order_id
        ) as DBT_INTERNAL_SOURCE
        on ((DBT_INTERNAL_SOURCE.order_id = DBT_INTERNAL_DEST.order_id))

    
    when matched then update set
        `order_id` = DBT_INTERNAL_SOURCE.`order_id`,`customer_id` = DBT_INTERNAL_SOURCE.`customer_id`,`store_id` = DBT_INTERNAL_SOURCE.`store_id`,`customer_name` = DBT_INTERNAL_SOURCE.`customer_name`,`customer_city` = DBT_INTERNAL_SOURCE.`customer_city`,`store_name` = DBT_INTERNAL_SOURCE.`store_name`,`store_city` = DBT_INTERNAL_SOURCE.`store_city`,`store_region` = DBT_INTERNAL_SOURCE.`store_region`,`store_type` = DBT_INTERNAL_SOURCE.`store_type`,`order_date` = DBT_INTERNAL_SOURCE.`order_date`,`order_amount` = DBT_INTERNAL_SOURCE.`order_amount`,`order_status` = DBT_INTERNAL_SOURCE.`order_status`,`total_quantity` = DBT_INTERNAL_SOURCE.`total_quantity`,`distinct_products` = DBT_INTERNAL_SOURCE.`distinct_products`,`item_subtotal` = DBT_INTERNAL_SOURCE.`item_subtotal`,`total_paid_amount` = DBT_INTERNAL_SOURCE.`total_paid_amount`,`successful_payment_count` = DBT_INTERNAL_SOURCE.`successful_payment_count`,`latest_payment_date` = DBT_INTERNAL_SOURCE.`latest_payment_date`,`payment_state` = DBT_INTERNAL_SOURCE.`payment_state`
    

    when not matched then insert
        (`order_id`, `customer_id`, `store_id`, `customer_name`, `customer_city`, `store_name`, `store_city`, `store_region`, `store_type`, `order_date`, `order_amount`, `order_status`, `total_quantity`, `distinct_products`, `item_subtotal`, `total_paid_amount`, `successful_payment_count`, `latest_payment_date`, `payment_state`)
    values
        (`order_id`, `customer_id`, `store_id`, `customer_name`, `customer_city`, `store_name`, `store_city`, `store_region`, `store_type`, `order_date`, `order_amount`, `order_status`, `total_quantity`, `distinct_products`, `item_subtotal`, `total_paid_amount`, `successful_payment_count`, `latest_payment_date`, `payment_state`)


    