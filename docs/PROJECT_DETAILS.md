# Project Details

This document keeps the deeper setup, validation, deployment, and handoff notes for the project. The main [README.md](/Users/woraphu/Documents/DBT/retail_bigquery_project_webapp/README.md) is intentionally shorter so it works better as the audience-facing project overview.

## What This App Does

- accepts a CSV upload where each row represents one order line
- saves uploaded rows into a BigQuery raw intake table
- runs dbt from the app after upload
- updates staging and fact models in BigQuery
- displays:
  - latest submitted record
  - pipeline observability
  - business KPI cards
  - revenue by store
  - dbt docs as a separate technical companion page

## What Problem It Solves

Many dbt projects stop at local models or static dashboards. This app shows a fuller workflow:

- ingestion through a web interface
- transformation with dbt
- storage in BigQuery
- presentation in a live dashboard
- technical visibility through dbt docs

It is designed for demo, portfolio, and interview showcasing rather than enterprise production hardening.

## Architecture

### High-Level Flow

```text
CSV Upload
   ->
FastAPI app
   ->
raw_webapp.json_submissions
   ->
stg_json_submissions
   ->
fct_submitted_orders
   ->
stg_orders / stg_order_items
   ->
fct_orders / fct_order_items
   ->
Dashboard + dbt docs
```

### User Workflow

```text
Choose CSV
   ->
Upload and Process
   ->
FastAPI saves rows to BigQuery
   ->
dbt run executes in the app environment
   ->
BigQuery tables update
   ->
Dashboard refresh shows new results
```

## Main Tools Used

- `FastAPI` for the app and endpoints
- `BigQuery` for raw, staging, and mart layers
- `dbt` for transformation logic and docs
- `Cloud Run` for deployment
- `Docker` for packaging the app and dbt runtime together
- `Chart.js` for the revenue chart

## Project Structure

```text
app/
  main.py
  bigquery_client.py
models/
  staging/
  marts/
macros/
data/
  raw_csv/
  sample_uploads/
dbt_project.yml
profiles.yml
packages.yml
load_raw_csv.sh
Dockerfile
requirements.txt
```

### Structure Notes

- `app/main.py`
  - FastAPI routes
  - dashboard HTML
  - CSV upload endpoint
  - dbt trigger logic
  - dbt docs mount at `/dbt-docs`
- `app/bigquery_client.py`
  - BigQuery write logic for uploaded CSV rows
  - BigQuery read logic for dashboard KPIs
  - latest submission and observability queries
- `models/staging/`
  - parses uploaded rows
  - merges uploaded data into the order and order-item flow
- `models/marts/`
  - final business-facing tables used by the dashboard
- `data/raw_csv/`
  - starter data loaded into the base raw tables
- `data/sample_uploads/`
  - demo CSV files for testing the upload flow
- `target/`
  - generated dbt artifacts
  - includes the static dbt docs snapshot used by the app
- `logs/`
  - dbt logs for local debugging
  - most useful when `dbt run`, `dbt test`, or `dbt docs generate` fails
- `secrets/`
  - local-only service account JSON key file
  - used by the local `dev` dbt target
- `snapshots/`
  - dbt snapshot definitions
  - currently includes `products_snapshot.sql`
- `sql/`
  - helper SQL files for BigQuery bootstrap work

### YAML And Lock File Guide

- `dbt_project.yml`
  - the main dbt project config
  - tells dbt where models, tests, macros, seeds, and snapshots are
  - also sets default materialization behavior for staging, intermediate, and marts
- `profiles.yml`
  - the real dbt connection config used by this repo
  - local `dev` uses a local JSON key file
  - `cloud_run` uses the Cloud Run runtime environment
- `profiles.yml.example`
  - a sample template for teammates or future handoff
  - useful when someone clones the repo and needs to create their own working `profiles.yml`
- `packages.yml`
  - lists dbt packages the project depends on
  - in this repo, the main package is `dbt_utils`
- `package-lock.yml`
  - the lock file created from `dbt deps`
  - records the exact resolved package version so installs stay consistent

## Important BigQuery Objects

### Raw

- `raw_webapp.customers`
- `raw_webapp.stores`
- `raw_webapp.products`
- `raw_webapp.orders`
- `raw_webapp.order_items`
- `raw_webapp.payments`
- `raw_webapp.json_submissions`

### Analytics

This showcase currently works against:

- `analytics_webapp_dev`

There are other outputs in `profiles.yml`, but for this demo the effective environment is `dev`.

### Core Tables In The App Flow

- `raw_webapp.json_submissions`
  - raw uploaded rows
  - one uploaded CSV row becomes one raw row
- `analytics_webapp_dev.stg_json_submissions`
  - parsed upload staging
- `analytics_webapp_dev.fct_submitted_orders`
  - incremental uploaded-order fact
  - one row per distinct uploaded order
- `analytics_webapp_dev.fct_orders`
  - main order-level business fact
- `analytics_webapp_dev.fct_order_items`
  - main order-line business fact

## BigQuery SQL Setup

### Create the upload intake table

Run this once in BigQuery if it does not already exist:

```sql
create table if not exists `retail-bigquery-project-webapp.raw_webapp.json_submissions` (
  submission_id string,
  submitted_at timestamp,
  payload_text string
);
```

### Load the base raw retail tables

This command loads the starter raw CSV files from `data/raw_csv/`:

```bash
./load_raw_csv.sh
```

It loads:

- `raw_webapp.customers`
- `raw_webapp.stores`
- `raw_webapp.products`
- `raw_webapp.orders`
- `raw_webapp.order_items`
- `raw_webapp.payments`

### Optional helper SQL

There is also a helper SQL file here:

- `sql/bootstrap_bigquery_raw_tables.sql`

Use it if you want a more explicit SQL-based bootstrap path in BigQuery in addition to the shell script.

## Local Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Load the base raw CSVs into BigQuery

```bash
./load_raw_csv.sh
```

### 3. Install dbt packages

```bash
dbt deps --profiles-dir .
```

### 4. Build the dbt models

```bash
dbt run --profiles-dir .
dbt test --profiles-dir .
```

### 5. Generate dbt docs

```bash
dbt docs generate --profiles-dir .
```

### 6. Run the web app locally

```bash
uvicorn app.main:app --reload
```

### 7. Open in the browser

- app: `http://127.0.0.1:8000/`
- dbt docs: `http://127.0.0.1:8000/dbt-docs`

## Local Demo Sequence

Use this order:

1. open the app
2. upload a CSV file from `data/sample_uploads/`
3. click `Upload and Process`
4. refresh the dashboard if needed
5. confirm:
   - latest submitted record updated
   - pipeline observability updated
   - business KPIs changed where expected

## Main dbt Commands Used

### Install dbt packages

```bash
dbt deps --profiles-dir .
```

### Full local build

```bash
dbt run --profiles-dir .
dbt test --profiles-dir .
```

### Generate docs snapshot

```bash
dbt docs generate --profiles-dir .
```

### Upload-and-process model run

The app triggers this logical build path after CSV upload:

```bash
dbt run --profiles-dir . --select stg_json_submissions fct_submitted_orders fct_orders fct_order_items
```

## Sample Upload File

Use:

- [data/sample_uploads/sample_order_upload.csv](/Users/woraphu/Documents/DBT/retail_bigquery_project_webapp/data/sample_uploads/sample_order_upload.csv)

This file includes multiple order lines for the same order so the retail workflow feels realistic.

## BigQuery Validation Queries

Use these after uploading a CSV and running the pipeline.

### 1. Raw uploaded rows

```sql
select
  submission_id,
  submitted_at,
  payload_text
from `retail-bigquery-project-webapp.raw_webapp.json_submissions`
order by submitted_at desc
limit 20;
```

### 2. Parsed staging rows

```sql
select *
from `retail-bigquery-project-webapp.analytics_webapp_dev.stg_json_submissions`
order by submitted_at desc
limit 20;
```

### 3. Uploaded-order incremental fact

```sql
select *
from `retail-bigquery-project-webapp.analytics_webapp_dev.fct_submitted_orders`
order by submitted_at desc
limit 20;
```

### 4. Check whether uploaded orders reached the main business fact

```sql
select *
from `retail-bigquery-project-webapp.analytics_webapp_dev.fct_orders`
where order_id in (91001, 91002)
order by order_id;
```

### 5. Check whether uploaded order lines reached the line-level business fact

```sql
select *
from `retail-bigquery-project-webapp.analytics_webapp_dev.fct_order_items`
where order_line_id in (9100101, 9100102, 9100103, 9100201, 9100202)
order by order_line_id;
```

### 6. KPI spot checks

```sql
select
  count(*) as total_orders,
  sum(order_amount) as total_revenue
from `retail-bigquery-project-webapp.analytics_webapp_dev.fct_orders`;
```

```sql
select
  count(*) as total_order_lines,
  sum(line_amount) as total_line_amount
from `retail-bigquery-project-webapp.analytics_webapp_dev.fct_order_items`;
```

```sql
select
  count(*) as submitted_orders,
  sum(order_amount) as submitted_revenue,
  max(order_date) as latest_submitted_order_date
from `retail-bigquery-project-webapp.analytics_webapp_dev.fct_submitted_orders`;
```

### How to read the counts

- raw submission count = uploaded line rows
- staged submission count = parsed uploaded line rows
- incremental fact count = distinct uploaded orders
- `Total Customers` and `Total Stores` come from dimension tables, so they do not automatically change from uploaded CSV rows in the current design

## Local Secret Setup

For local dbt runs, the `dev` target currently expects a service account JSON key file in:

```text
secrets/retail-bigquery-project-webapp-11cb2b57ecb4.json
```

### How to create the local key in GCP

1. open `IAM & Admin`
2. open `Service Accounts`
3. create or select the service account you want to use locally
4. open the `Keys` tab
5. click `Add Key`
6. choose `Create new key`
7. choose `JSON`
8. download the file
9. place it in the local `secrets/` folder

Important:

- do not commit the JSON key file
- `secrets/` should stay ignored
- Cloud Run does not use this local key file

## Cloud Run Roles And Permissions

### Runtime service account

The deployed app uses this runtime service account:

```text
dbt-webapp-runner@retail-bigquery-project-webapp.iam.gserviceaccount.com
```

For the current design, the runtime service account should be able to:

- read source and mart tables
- create or replace dbt-built tables
- run BigQuery jobs

The most important BigQuery roles to check are:

- `BigQuery Data Editor`
- `BigQuery Job User`
- `BigQuery Data Viewer`

### Deployer permissions

The user deploying from local usually needs permissions equivalent to:

- `Cloud Run Admin`
- `Service Account User`
- `Cloud Build Editor`
- `Artifact Registry Writer`

Depending on project setup, exact scope may vary, but these are the first roles to verify.

## Cloud Run Deployment

### What Cloud Run Needs

The deployed container must include:

- the web app code
- dbt itself
- dbt project files
- generated dbt docs in `target/`

That is why the deployment setup includes:

- `dbt-bigquery` in `requirements.txt`
- dbt files copied in `Dockerfile`
- `target/` copied into the image for `/dbt-docs`

### Deployment Steps

#### 1. Regenerate dbt docs locally before deploy

```bash
dbt docs generate --profiles-dir .
```

#### 2. Deploy to Cloud Run

```bash
gcloud run deploy retail-bigquery-webapp-api \
  --source . \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --service-account dbt-webapp-runner@retail-bigquery-project-webapp.iam.gserviceaccount.com \
  --set-env-vars GCP_PROJECT_ID=retail-bigquery-project-webapp,BQ_DATASET=analytics_webapp_dev \
  --memory 2Gi \
  --cpu 1 \
  --timeout 300 \
  --port 8080
```

#### 3. Validate the deployed app

Check:

- homepage loads
- CSV upload works
- `Upload and Process` works
- dbt docs page opens

Useful links:

- app:
  `https://retail-bigquery-webapp-api-863751637669.asia-southeast1.run.app/`
- dbt docs:
  `https://retail-bigquery-webapp-api-863751637669.asia-southeast1.run.app/dbt-docs`

## Local vs Cloud Run

### Local

- easiest place to test changes first
- uses your local `dev` profile
- best for debugging dbt and UI quickly

### Cloud Run

- serves the deployed version only
- only updates after a successful redeploy
- needs the dbt runtime and docs snapshot packaged into the image

Simple rule:

```text
Code change
  ->
Test locally
  ->
Regenerate docs if dbt changed
  ->
Redeploy to Cloud Run
```

## dbt Docs Notes

The dbt docs page is served as a static snapshot.

That means:

- when models or descriptions change, run:

```bash
dbt docs generate --profiles-dir .
```

- then redeploy if you want the Cloud Run docs page updated too

## Snapshot Note

This repo still contains:

- `snapshots/products_snapshot.sql`

That snapshot is not central to the current web demo, but it can still affect dbt docs generation. Earlier, `dbt docs generate` warned about a missing `snapshots` dataset in BigQuery.

So if you keep snapshots in the repo, make sure the matching BigQuery dataset exists.

If snapshots are not part of the final showcase story, this is one area worth reviewing later for cleanup.

## Cleanup Review

You asked a good question about unused tables. I do suspect there may be some leftover or experimental objects from earlier iterations, especially around snapshots.

I do not recommend deleting anything blindly. Review first.

### List raw dataset tables

```sql
select
  table_name,
  table_type
from `retail-bigquery-project-webapp.raw_webapp.INFORMATION_SCHEMA.TABLES`
order by table_name;
```

### List analytics dev dataset tables

```sql
select
  table_name,
  table_type
from `retail-bigquery-project-webapp.analytics_webapp_dev.INFORMATION_SCHEMA.TABLES`
order by table_name;
```

### Check whether a snapshots dataset exists

```sql
select
  schema_name
from `retail-bigquery-project-webapp.region-asia-southeast1.INFORMATION_SCHEMA.SCHEMATA`
where schema_name = 'snapshots';
```

### Likely review candidates

- snapshot-related datasets or tables if snapshots are not part of the final demo
- old experimental tables created outside the current dbt model set

### If you decide the snapshots dataset is not needed

Use this only after review:

```sql
drop schema `retail-bigquery-project-webapp.snapshots` cascade;
```

## Workflow Summary

### Local Workflow

```text
Install deps
  ->
Load base raw CSVs into BigQuery
  ->
dbt deps / dbt run / dbt test
  ->
dbt docs generate
  ->
run FastAPI locally
  ->
upload CSV and validate
```

### Cloud Run Workflow

```text
Finish local changes
  ->
dbt docs generate
  ->
gcloud run deploy
  ->
test live app
  ->
test live /dbt-docs
```

## Current Scope

### Included

- CSV upload workflow
- one-button upload + process flow
- BigQuery raw intake
- dbt staging and mart updates
- business KPIs and pipeline observability
- separate dbt docs page

### Not Included Yet

- full automatic async orchestration after upload
- CI/CD pipeline
- auth / role-based access
- dimension expansion from uploaded new customers or new stores

## Notes for Future Handoff

- the app currently showcases the `dev` environment
- `Total Customers` and `Total Stores` come from dimension tables, so uploaded CSVs do not automatically increase those counts unless the dimension pipeline is extended
- uploaded CSV rows do affect:
  - `fct_submitted_orders`
  - `fct_orders`
  - `fct_order_items`

## Why This Project Is Strong for Showcasing

This repo demonstrates:

- analytics engineering with dbt and BigQuery
- containerized deployment on Cloud Run
- data ingestion through a real web app
- a bridge between business-facing dashboards and technical lineage/docs

It is intended to be understandable to both:

- non-technical reviewers
- technical data teams
