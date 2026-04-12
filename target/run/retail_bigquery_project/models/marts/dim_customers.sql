
  
    

    create or replace table `bq-test-query`.`analytics_dev`.`dim_customers`
      
    
    

    
    OPTIONS()
    as (
      

-- Build a customer dimension with summarized order history metrics.
select
  c.customer_id,
  c.customer_name,
  c.email,
  c.city,
  c.signup_date,
  min(o.order_date) as first_order_date,
  max(o.order_date) as latest_order_date,
  count(distinct o.order_id) as total_orders,
  coalesce(cast(sum(o.order_amount) as numeric), 0) as lifetime_order_value
from `bq-test-query`.`analytics_dev`.`stg_customers` c
left join `bq-test-query`.`analytics_dev`.`stg_orders` o
  on c.customer_id = o.customer_id
group by
  c.customer_id,
  c.customer_name,
  c.email,
  c.city,
  c.signup_date
    );
  