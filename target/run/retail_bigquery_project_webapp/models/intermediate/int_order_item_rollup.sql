

  create or replace view `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`int_order_item_rollup`
  OPTIONS()
  as 

-- Roll order lines back up to the order grain for order-level reporting.
select
  order_id,
  sum(quantity) as total_quantity,
  count(distinct product_id) as distinct_products,
  cast(sum(line_amount) as numeric) as item_subtotal
from `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`stg_order_items`
group by order_id;

