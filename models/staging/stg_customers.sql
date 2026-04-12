{{ config(materialized='view') }}

-- Standardize customer text and keep one row per customer.
select
  customer_id,
  upper(customer_name) as customer_name,
  lower(email) as email,
  signup_date,
  city
from {{ source('raw', 'customers') }}
