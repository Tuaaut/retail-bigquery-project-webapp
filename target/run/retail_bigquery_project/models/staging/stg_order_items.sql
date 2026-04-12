

  create or replace view `bq-test-query`.`analytics_dev`.`stg_order_items`
  OPTIONS()
  as 

-- Normalize order lines at one row per item in each order.
select
  order_line_id,
  order_id,
  product_id,
  cast(quantity as int64) as quantity,
  cast(unit_price as numeric) as unit_price,
  cast(line_amount as numeric) as line_amount
from `bq-test-query`.`raw`.`order_items`;

