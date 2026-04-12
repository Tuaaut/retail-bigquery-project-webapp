

  create or replace view `retail-bigquery-project-webapp`.`analytics_webapp_dev`.`stg_json_submissions`
  OPTIONS()
  as select
  submission_id,
  submitted_at,
  payload_text,

  cast(json_value(payload_text, '$.order_id') as int64) as order_id,
  cast(json_value(payload_text, '$.customer_id') as int64) as customer_id,
  cast(json_value(payload_text, '$.store_id') as int64) as store_id,
  cast(json_value(payload_text, '$.order_date') as date) as order_date,
  cast(json_value(payload_text, '$.order_amount') as numeric) as order_amount,
  lower(json_value(payload_text, '$.order_status')) as order_status,
  cast(json_value(payload_text, '$.order_line_id') as int64) as order_line_id,
  cast(json_value(payload_text, '$.product_id') as int64) as product_id,
  cast(json_value(payload_text, '$.quantity') as int64) as quantity,
  cast(json_value(payload_text, '$.unit_price') as numeric) as unit_price,
  cast(json_value(payload_text, '$.line_amount') as numeric) as line_amount

from `retail-bigquery-project-webapp`.`raw_webapp`.`json_submissions`;

