{{ config(materialized='view') }}

-- Roll order lines back up to the order grain for order-level reporting.
select
  order_id,
  sum(quantity) as total_quantity,
  count(distinct product_id) as distinct_products,
  cast(sum(line_amount) as numeric) as item_subtotal
from {{ ref('stg_order_items') }}
group by order_id
