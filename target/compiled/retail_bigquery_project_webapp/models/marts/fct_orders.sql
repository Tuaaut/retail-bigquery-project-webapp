

-- Build the order-level fact table and only reprocess recent order dates on incremental runs.
with order_scope as (
  select *
  from `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`int_orders_enriched`

  
    -- Re-read the latest loaded order date so merge can update late-arriving changes safely.
    where order_date >= (select coalesce(max(order_date), date('1900-01-01')) from `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`fct_orders`)
  
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
left join `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`int_order_item_rollup` r
  on o.order_id = r.order_id
left join `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`int_order_payments` p
  on o.order_id = p.order_id