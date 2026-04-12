

  create or replace view `bq-test-query`.`analytics_dev`.`int_order_item_rollup`
  OPTIONS()
  as 

-- Roll order lines back up to the order grain for order-level reporting.
select
  order_id,
  sum(quantity) as total_quantity,
  count(distinct product_id) as distinct_products,
  cast(sum(line_amount) as numeric) as item_subtotal
from `bq-test-query`.`analytics_dev`.`stg_order_items`
group by order_id;

