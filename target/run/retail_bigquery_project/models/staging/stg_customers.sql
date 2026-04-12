

  create or replace view `bq-test-query`.`analytics_dev`.`stg_customers`
  OPTIONS()
  as 

-- Standardize customer text and keep one row per customer.
select
  customer_id,
  upper(customer_name) as customer_name,
  lower(email) as email,
  signup_date,
  city
from `bq-test-query`.`raw`.`customers`;

