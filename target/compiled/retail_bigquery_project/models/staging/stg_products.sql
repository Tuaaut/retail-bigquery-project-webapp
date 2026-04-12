

-- Standardize product text fields and pricing columns.
select
  product_id,
  upper(product_name) as product_name,
  lower(category) as category,
  lower(brand) as brand,
  cast(base_price as numeric) as base_price
from `bq-test-query`.`raw`.`products`