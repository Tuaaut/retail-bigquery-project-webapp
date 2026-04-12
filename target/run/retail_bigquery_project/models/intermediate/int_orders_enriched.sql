

  create or replace view `bq-test-query`.`analytics_dev`.`int_orders_enriched`
  OPTIONS()
  as 

-- Join order headers to customer and store attributes at one row per order.
select
  o.order_id,
  o.customer_id,
  o.store_id,
  c.customer_name,
  c.email,
  c.city as customer_city,
  c.signup_date,
  s.store_name,
  s.city as store_city,
  s.region as store_region,
  s.store_type,
  o.order_date,
  o.order_amount,
  o.order_status
from `bq-test-query`.`analytics_dev`.`stg_orders` o
left join `bq-test-query`.`analytics_dev`.`stg_customers` c
  on o.customer_id = c.customer_id
left join `bq-test-query`.`analytics_dev`.`stg_stores` s
  on o.store_id = s.store_id;

