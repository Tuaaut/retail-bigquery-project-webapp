#!/usr/bin/env bash
set -e

# Load exported raw CSV files into the BigQuery raw dataset.
bq --location=asia-southeast1 load --source_format=CSV --skip_leading_rows=1 retail-bigquery-project-webapp:raw_webapp.customers ./data/raw_csv/customers.csv
bq --location=asia-southeast1 load --source_format=CSV --skip_leading_rows=1 retail-bigquery-project-webapp:raw_webapp.stores ./data/raw_csv/stores.csv
bq --location=asia-southeast1 load --source_format=CSV --skip_leading_rows=1 retail-bigquery-project-webapp:raw_webapp.products ./data/raw_csv/products.csv
bq --location=asia-southeast1 load --source_format=CSV --skip_leading_rows=1 retail-bigquery-project-webapp:raw_webapp.orders ./data/raw_csv/orders.csv
bq --location=asia-southeast1 load --source_format=CSV --skip_leading_rows=1 retail-bigquery-project-webapp:raw_webapp.order_items ./data/raw_csv/order_items.csv
bq --location=asia-southeast1 load --source_format=CSV --skip_leading_rows=1 retail-bigquery-project-webapp:raw_webapp.payments ./data/raw_csv/payments.csv
