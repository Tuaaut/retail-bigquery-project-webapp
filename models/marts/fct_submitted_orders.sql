{{
  config(
    materialized='incremental',
    unique_key='order_id',
    on_schema_change='sync_all_columns'
  )
}}

with submitted_orders as (
  select
    submission_id,
    submitted_at,
    order_id,
    customer_id,
    store_id,
    order_date,
    order_amount,
    order_status,
    row_number() over (
      partition by order_id
      order by submitted_at desc, submission_id desc
    ) as row_num
  from {{ ref('stg_json_submissions') }}
  where order_id is not null
)

select
  submission_id,
  submitted_at,
  order_id,
  customer_id,
  store_id,
  order_date,
  order_amount,
  order_status

from submitted_orders

where row_num = 1

{% if is_incremental() %}
  and submitted_at > (
    select coalesce(max(submitted_at), timestamp('1900-01-01'))
    from {{ this }}
  )
{% endif %}
