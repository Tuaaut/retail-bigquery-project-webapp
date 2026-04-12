

  create or replace view `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`stg_customers`
  OPTIONS()
  as 

-- Standardize customer text and keep one row per customer.
select
  customer_id,
  upper(customer_name) as customer_name,
  lower(email) as email,
  signup_date,
  city
from `retail-bigquery-project-webapp`.`raw_webapp`.`customers`;

