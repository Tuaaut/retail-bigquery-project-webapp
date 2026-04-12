

-- Build a store dimension with summarized order activity by store.
select
  s.store_id,
  s.store_name,
  s.city,
  s.region,
  s.opened_date,
  s.store_type,
  count(distinct o.order_id) as total_orders,
  coalesce(cast(sum(o.order_amount) as numeric), 0) as total_order_value,
  min(o.order_date) as first_order_date,
  max(o.order_date) as latest_order_date
from `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`stg_stores` s
left join `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`stg_orders` o
  on s.store_id = o.store_id
group by
  s.store_id,
  s.store_name,
  s.city,
  s.region,
  s.opened_date,
  s.store_type