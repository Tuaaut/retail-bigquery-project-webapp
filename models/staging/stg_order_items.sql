{{ config(materialized='view') }}

with raw_order_items as (
  select
    order_line_id,
    order_id,
    product_id,
    cast(quantity as int64) as quantity,
    cast(unit_price as numeric) as unit_price,
    cast(line_amount as numeric) as line_amount,
    cast(null as timestamp) as submitted_at,
    1 as source_priority
  from {{ source('raw', 'order_items') }}
),

submitted_order_items as (
  select
    order_line_id,
    order_id,
    product_id,
    quantity,
    unit_price,
    line_amount,
    submitted_at,
    2 as source_priority
  from {{ ref('stg_json_submissions') }}
  where order_line_id is not null
),

combined_order_items as (
  select * from raw_order_items
  union all
  select * from submitted_order_items
)

select
  order_line_id,
  order_id,
  product_id,
  quantity,
  unit_price,
  line_amount
from combined_order_items
qualify row_number() over (
  partition by order_line_id
  order by source_priority desc, submitted_at desc nulls last
) = 1
