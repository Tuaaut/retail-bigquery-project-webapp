

-- Aggregate payment records up to the order grain.
select
  order_id,
  sum(case when payment_status = 'paid' then payment_amount else 0 end) as total_paid_amount,
  countif(payment_status = 'paid') as successful_payment_count,
  max(payment_date) as latest_payment_date
from `bq-test-query`.`analytics_dev`.`stg_payments`
group by order_id