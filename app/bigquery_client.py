import csv
import io
import json
import os
import uuid
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from google.cloud import bigquery

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "retail-bigquery-project-webapp")
DATASET = os.getenv("BQ_DATASET", "analytics_webapp_dev")
RAW_DATASET = os.getenv("BQ_RAW_DATASET", "raw_webapp")
SUBMISSION_TABLE = os.getenv("BQ_SUBMISSION_TABLE", "json_submissions")


def _client() -> bigquery.Client:
    return bigquery.Client(project=PROJECT_ID)


def get_summary_metrics() -> dict:
    client = _client()

    query = f"""
    with orders_summary as (
      select
        count(*) as total_orders,
        cast(coalesce(sum(order_amount), 0) as numeric) as total_revenue
      from `{PROJECT_ID}.{DATASET}.fct_orders`
    ),
    order_items_summary as (
      select count(*) as total_order_lines
      from `{PROJECT_ID}.{DATASET}.fct_order_items`
    ),
    customers_summary as (
      select count(*) as total_customers
      from `{PROJECT_ID}.{DATASET}.dim_customers`
    ),
    stores_summary as (
      select count(*) as total_stores
      from `{PROJECT_ID}.{DATASET}.dim_stores`
    )
    select
      c.total_customers,
      s.total_stores,
      o.total_orders,
      oi.total_order_lines,
      o.total_revenue
    from customers_summary c
    cross join stores_summary s
    cross join orders_summary o
    cross join order_items_summary oi
    """

    rows = list(client.query(query).result())
    if not rows:
        return {
            "project_id": PROJECT_ID,
            "dataset": DATASET,
            "total_customers": 0,
            "total_stores": 0,
            "total_orders": 0,
            "total_order_lines": 0,
            "total_revenue": "0",
        }

    row = rows[0]
    return {
        "project_id": PROJECT_ID,
        "dataset": DATASET,
        "total_customers": row["total_customers"],
        "total_stores": row["total_stores"],
        "total_orders": row["total_orders"],
        "total_order_lines": row["total_order_lines"],
        "total_revenue": str(row["total_revenue"]),
    }


def get_revenue_by_store() -> list[dict]:
    client = _client()

    query = f"""
    select
      store_name,
      round(sum(order_amount), 2) as revenue
    from `{PROJECT_ID}.{DATASET}.fct_orders`
    group by store_name
    order by revenue desc
    """

    rows = client.query(query).result()
    return [
        {
            "store_name": row["store_name"],
            "revenue": float(row["revenue"] or 0),
        }
        for row in rows
    ]


def get_last_refresh_timestamp() -> str:
    client = _client()

    query = f"""
    select
      max(last_modified_time) as last_modified_at
    from `{PROJECT_ID}.{DATASET}.__TABLES__`
    where table_id in ('fct_orders', 'fct_order_items')
    """

    rows = list(client.query(query).result())
    if not rows:
        return "Unavailable"

    ts = rows[0]["last_modified_at"]
    if ts is None:
        return "Unavailable"

    bangkok_tz = ZoneInfo("Asia/Bangkok")

    if isinstance(ts, (int, float)):
        dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        return dt.astimezone(bangkok_tz).strftime("%Y-%m-%d %H:%M:%S ICT")

    if isinstance(ts, datetime):
        return ts.astimezone(bangkok_tz).strftime("%Y-%m-%d %H:%M:%S ICT")

    return str(ts)


def save_json_submission(payload_text: str) -> dict:
    client = _client()

    parsed = json.loads(payload_text)

    submission_id = str(uuid.uuid4())
    submitted_at = datetime.now(timezone.utc)

    table_id = f"{PROJECT_ID}.{RAW_DATASET}.{SUBMISSION_TABLE}"
    rows = [
        {
            "submission_id": submission_id,
            "submitted_at": submitted_at.isoformat(),
            "payload_text": json.dumps(parsed, ensure_ascii=False),
        }
    ]

    errors = client.insert_rows_json(table_id, rows)
    if errors:
        raise ValueError(f"BigQuery insert failed: {errors}")

    bangkok_tz = ZoneInfo("Asia/Bangkok")
    submitted_at_bangkok = submitted_at.astimezone(bangkok_tz).strftime("%Y-%m-%d %H:%M:%S ICT")

    return {
        "submission_id": submission_id,
        "submitted_at": submitted_at_bangkok,
    }


def save_csv_submissions(file_bytes: bytes) -> dict:
    text = file_bytes.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))

    required_columns = {
        "order_id",
        "customer_id",
        "store_id",
        "order_date",
        "order_amount",
        "order_status",
        "order_line_id",
        "product_id",
        "quantity",
        "unit_price",
        "line_amount",
    }

    if not reader.fieldnames:
        raise ValueError("CSV file is empty or missing headers.")

    missing_columns = sorted(required_columns - set(reader.fieldnames))
    if missing_columns:
        raise ValueError(
            "CSV is missing required columns: " + ", ".join(missing_columns)
        )

    rows_to_insert = []
    submitted_at = datetime.now(timezone.utc)

    for raw_row in reader:
        if not any((value or "").strip() for value in raw_row.values()):
            continue

        payload = {
            "order_id": raw_row["order_id"],
            "customer_id": raw_row["customer_id"],
            "store_id": raw_row["store_id"],
            "order_date": raw_row["order_date"],
            "order_amount": raw_row["order_amount"],
            "order_status": raw_row["order_status"],
            "order_line_id": raw_row["order_line_id"],
            "product_id": raw_row["product_id"],
            "quantity": raw_row["quantity"],
            "unit_price": raw_row["unit_price"],
            "line_amount": raw_row["line_amount"],
        }

        rows_to_insert.append(
            {
                "submission_id": str(uuid.uuid4()),
                "submitted_at": submitted_at.isoformat(),
                "payload_text": json.dumps(payload, ensure_ascii=False),
            }
        )

    if not rows_to_insert:
        raise ValueError("CSV file has no data rows to upload.")

    client = _client()
    table_id = f"{PROJECT_ID}.{RAW_DATASET}.{SUBMISSION_TABLE}"
    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors:
        raise ValueError(f"BigQuery insert failed: {errors}")

    bangkok_tz = ZoneInfo("Asia/Bangkok")
    submitted_at_bangkok = submitted_at.astimezone(bangkok_tz).strftime("%Y-%m-%d %H:%M:%S ICT")

    return {
        "row_count": len(rows_to_insert),
        "submitted_at": submitted_at_bangkok,
    }

def get_latest_submission() -> dict:
    client = _client()

    query = f"""
    select
      submission_id,
      submitted_at,
      payload_text
    from `{PROJECT_ID}.{RAW_DATASET}.{SUBMISSION_TABLE}`
    order by submitted_at desc
    limit 1
    """

    rows = list(client.query(query).result())
    if not rows:
        return {
            "submission_id": "Unavailable",
            "submitted_at": "Unavailable",
            "fields": {}
        }

    row = rows[0]
    bangkok_tz = ZoneInfo("Asia/Bangkok")

    submitted_at = row["submitted_at"]
    if isinstance(submitted_at, datetime):
        submitted_at = submitted_at.astimezone(bangkok_tz).strftime("%Y-%m-%d %H:%M:%S ICT")
    else:
        submitted_at = str(submitted_at)

    try:
        payload = json.loads(row["payload_text"])
    except Exception:
        payload = {"raw_payload": row["payload_text"]}

    return {
        "submission_id": row["submission_id"],
        "submitted_at": submitted_at,
        "fields": payload,
    }

def get_submitted_orders_metrics() -> dict:
    client = _client()

    query = f"""
    select
      count(*) as total_submitted_orders,
      cast(coalesce(sum(order_amount), 0) as numeric) as submitted_revenue,
      max(order_date) as latest_submitted_order_date
    from `{PROJECT_ID}.{DATASET}.fct_submitted_orders`
    """

    rows = list(client.query(query).result())
    if not rows:
        return {
            "total_submitted_orders": 0,
            "submitted_revenue": "0",
            "latest_submitted_order_date": "Unavailable",
        }

    row = rows[0]
    latest_order_date = row["latest_submitted_order_date"]
    if latest_order_date is None:
        latest_order_date = "Unavailable"
    else:
        latest_order_date = str(latest_order_date)

    return {
        "total_submitted_orders": row["total_submitted_orders"],
        "submitted_revenue": str(row["submitted_revenue"]),
        "latest_submitted_order_date": latest_order_date,
    }

def get_pipeline_observability_metrics() -> dict:
    client = _client()

    query = f"""
    with raw_stats as (
      select
        count(*) as raw_submission_count,
        max(submitted_at) as latest_raw_submission_at
      from `{PROJECT_ID}.{RAW_DATASET}.{SUBMISSION_TABLE}`
    ),
    staging_stats as (
      select
        count(*) as staged_submission_count
      from `{PROJECT_ID}.{DATASET}.stg_json_submissions`
    ),
    fact_stats as (
      select
        count(*) as fact_submission_count,
        max(submitted_at) as latest_fact_submission_at
      from `{PROJECT_ID}.{DATASET}.fct_submitted_orders`
    )
    select
      raw_stats.raw_submission_count,
      raw_stats.latest_raw_submission_at,
      staging_stats.staged_submission_count,
      fact_stats.fact_submission_count,
      fact_stats.latest_fact_submission_at
    from raw_stats
    cross join staging_stats
    cross join fact_stats
    """

    rows = list(client.query(query).result())
    if not rows:
        return {
            "raw_submission_count": 0,
            "staged_submission_count": 0,
            "fact_submission_count": 0,
            "latest_raw_submission_at": "Unavailable",
            "latest_fact_submission_at": "Unavailable",
        }

    row = rows[0]
    bangkok_tz = ZoneInfo("Asia/Bangkok")

    def format_ts(value):
        if value is None:
            return "Unavailable"
        if isinstance(value, datetime):
            return value.astimezone(bangkok_tz).strftime("%Y-%m-%d %H:%M:%S ICT")
        return str(value)

    return {
        "raw_submission_count": row["raw_submission_count"],
        "staged_submission_count": row["staged_submission_count"],
        "fact_submission_count": row["fact_submission_count"],
        "latest_raw_submission_at": format_ts(row["latest_raw_submission_at"]),
        "latest_fact_submission_at": format_ts(row["latest_fact_submission_at"]),
    }

