

with raw_orders as (
  select
    order_id,
    customer_id,
    store_id,
    cast(order_date as date) as order_date,
    cast(order_amount as numeric) as order_amount,
    lower(order_status) as order_status,
    cast(null as timestamp) as submitted_at,
    1 as source_priority
  from `retail-bigquery-project-webapp`.`raw_webapp`.`orders`
),

submitted_orders as (
  select
    order_id,
    customer_id,
    store_id,
    order_date,
    order_amount,
    order_status,
    submitted_at,
    2 as source_priority
  from `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`stg_json_submissions`
  where order_id is not null
),

combined_orders as (
  select * from raw_orders
  union all
  select * from submitted_orders
)

select
  order_id,
  customer_id,
  store_id,
  order_date,
  order_amount,
  order_status
from combined_orders
qualify row_number() over (
  partition by order_id
  order by source_priority desc, submitted_at desc nulls last
) = 1