# Retail BigQuery Webapp

Live app: `https://retail-bigquery-webapp-api-863751637669.asia-southeast1.run.app/`

A portfolio-style data application that turns a dbt + BigQuery project into a usable product. The app accepts a retail CSV upload, lands the data in BigQuery, runs dbt transformations, and surfaces both business KPIs and technical pipeline visibility in one place.

## Why This Project Matters

Many analytics projects stop at SQL models or dashboards. This one shows the full path:

- data intake through a web interface
- transformation with dbt
- warehouse storage in BigQuery
- KPI presentation for non-technical users
- dbt docs for technical transparency

It is designed to be easy to demo to hiring managers, stakeholders, and data teams.

## What The Viewer Sees

- a FastAPI dashboard for retail analytics
- CSV upload and one-click processing
- KPI cards and revenue-by-store chart
- latest submitted record and pipeline observability metrics
- a separate `/dbt-docs` page for lineage and model documentation

## End-To-End Workflow

```text
Retail CSV
   |
   v
FastAPI upload endpoint
   |
   v
BigQuery raw intake table
   |
   v
dbt transformations
   |
   +--> staging models
   |
   +--> marts / facts
   |
   v
Dashboard metrics + dbt docs
```

## Architecture Snapshot

```text
Browser
  |
  v
FastAPI app
  |
  +--> BigQuery reads for dashboard metrics
  |
  +--> BigQuery writes for uploaded CSV rows
  |
  +--> dbt run for selected models
  |
  v
Cloud Run container
  |
  +--> dbt project files
  +--> generated dbt docs in target/
```

## Stack

- `FastAPI` for the web application
- `dbt` for transformation logic and docs
- `BigQuery` for raw, staging, and mart layers
- `Cloud Run` for deployment
- `Docker` for packaging the app runtime
- `Chart.js` for the dashboard visualization

## Key Project Areas

```text
app/                    FastAPI app, routes, dashboard UI
models/staging/         dbt staging logic
models/marts/           dbt marts and facts
data/sample_uploads/    demo CSV files
target/                 generated dbt docs artifacts
Dockerfile              container build definition
```

## Demo Flow

1. Open the live app.
2. Upload `data/sample_uploads/sample_order_upload.csv`.
3. Click `Upload and Process`.
4. Show the KPI and pipeline sections updating.
5. Open `/dbt-docs` to show lineage and technical documentation.

## Local Quick Start

```bash
pip install -r requirements.txt
./load_raw_csv.sh
dbt deps --profiles-dir .
dbt run --profiles-dir .
dbt test --profiles-dir .
dbt docs generate --profiles-dir .
uvicorn app.main:app --reload
```

Local URLs:

- app: `http://127.0.0.1:8000/`
- dbt docs: `http://127.0.0.1:8000/dbt-docs`

## Audience Notes

- For non-technical viewers, this project shows how raw business data becomes useful metrics.
- For technical viewers, it shows dbt model flow, Cloud Run packaging, and warehouse-backed app behavior.
- The current demo focuses on a clear showcase experience rather than enterprise production hardening.

## More Detail

The full setup, validation queries, secret handling, and deployment notes now live in:

- [docs/PROJECT_DETAILS.md](/Users/woraphu/Documents/DBT/retail_bigquery_project_webapp/docs/PROJECT_DETAILS.md)
