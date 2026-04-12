{{
  config(
    materialized='incremental',
    unique_key='order_line_id',
    incremental_strategy='merge',
    partition_by={
      "field": "order_date",
      "data_type": "date"
    },
    cluster_by=['order_id', 'product_id']
  )
}}

-- Build the item-level fact table and only reprocess recent order dates on incremental runs.
with item_scope as (
  select *
  from {{ ref('int_order_item_enriched') }}

  {% if is_incremental() %}
    -- Re-read the latest loaded order date so merge can update late-arriving order lines safely.
    where order_date >= (select coalesce(max(order_date), date('1900-01-01')) from {{ this }})
  {% endif %}
)

select
  i.order_line_id,
  i.order_id,
  i.customer_id,
  i.store_id,
  i.product_id,
  i.order_date,
  i.order_status,
  c.customer_name,
  c.city as customer_city,
  s.store_name,
  s.city as store_city,
  s.region as store_region,
  p.product_name,
  p.category,
  p.brand,
  i.quantity,
  i.unit_price,
  i.line_amount
from item_scope i
left join {{ ref('stg_customers') }} c
  on i.customer_id = c.customer_id
left join {{ ref('stg_stores') }} s
  on i.store_id = s.store_id
left join {{ ref('stg_products') }} p
  on i.product_id = p.product_id
