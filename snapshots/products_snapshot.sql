{% snapshot products_snapshot %}

{{
  config(
    target_schema='snapshots',
    unique_key='product_id',
    strategy='check',
    check_cols=['product_name', 'category', 'brand', 'base_price']
  )
}}

-- Keep historical versions of product records whenever tracked attributes change.
select
  product_id,
  product_name,
  category,
  brand,
  base_price
from {{ source('raw', 'products') }}

{% endsnapshot %}
