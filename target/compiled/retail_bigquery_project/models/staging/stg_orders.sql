

-- Normalize order headers at one row per order.
select
  order_id,
  customer_id,
  store_id,
  cast(order_date as date) as order_date,
  cast(order_amount as numeric) as order_amount,
  lower(order_status) as order_status
from `bq-test-query`.`raw`.`orders`