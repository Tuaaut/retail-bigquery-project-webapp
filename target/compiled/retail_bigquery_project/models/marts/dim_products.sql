

-- Build a product dimension with summarized sales metrics by product.
select
  p.product_id,
  p.product_name,
  p.category,
  p.brand,
  p.base_price,
  coalesce(sum(i.quantity), 0) as total_quantity_sold,
  coalesce(cast(sum(i.line_amount) as numeric), 0) as total_sales_amount,
  min(i.order_date) as first_order_date,
  max(i.order_date) as latest_order_date
from `bq-test-query`.`analytics_dev`.`stg_products` p
left join `bq-test-query`.`analytics_dev`.`int_order_item_enriched` i
  on p.product_id = i.product_id
group by
  p.product_id,
  p.product_name,
  p.category,
  p.brand,
  p.base_price