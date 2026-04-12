{{ config(materialized='view') }}

-- Standardize store attributes before downstream joins.
select
  store_id,
  upper(store_name) as store_name,
  city,
  lower(region) as region,
  opened_date,
  lower(store_type) as store_type
from {{ source('raw', 'stores') }}
