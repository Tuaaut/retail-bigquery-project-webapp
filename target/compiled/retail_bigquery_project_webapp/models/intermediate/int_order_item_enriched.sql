

-- Join order lines to order headers and product master attributes.
select
  oi.order_line_id,
  oi.order_id,
  o.customer_id,
  o.store_id,
  o.order_date,
  o.order_status,
  oi.product_id,
  p.product_name,
  p.category,
  p.brand,
  oi.quantity,
  oi.unit_price,
  oi.line_amount
from `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`stg_order_items` oi
left join `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`stg_orders` o
  on oi.order_id = o.order_id
left join `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`stg_products` p
  on oi.product_id = p.product_id