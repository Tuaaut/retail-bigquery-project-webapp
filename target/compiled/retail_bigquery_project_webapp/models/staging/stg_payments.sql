

-- Normalize payment records before building payment rollups.
select
  payment_id,
  order_id,
  cast(payment_date as date) as payment_date,
  cast(payment_amount as numeric) as payment_amount,
  lower(payment_method) as payment_method,
  lower(payment_status) as payment_status
from `retail-bigquery-project-webapp`.`raw_webapp`.`payments`