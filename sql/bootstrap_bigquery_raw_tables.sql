-- Run this script in BigQuery first to create the raw dataset and base tables.

create schema if not exists `retail-bigquery-project-webapp.raw_webapp`;

create table if not exists `retail-bigquery-project-webapp.raw_webapp.customers` (
  customer_id int64,
  customer_name string,
  email string,
  signup_date date,
  city string
);

create table if not exists `retail-bigquery-project-webapp.raw_webapp.stores` (
  store_id int64,
  store_name string,
  city string,
  region string,
  opened_date date,
  store_type string
);

create table if not exists `retail-bigquery-project-webapp.raw_webapp.products` (
  product_id int64,
  product_name string,
  category string,
  brand string,
  base_price numeric
);

create table if not exists `retail-bigquery-project-webapp.raw_webapp.orders` (
  order_id int64,
  customer_id int64,
  store_id int64,
  order_date date,
  order_amount numeric,
  order_status string
);

create table if not exists `retail-bigquery-project-webapp.raw_webapp.order_items` (
  order_line_id int64,
  order_id int64,
  product_id int64,
  quantity int64,
  unit_price numeric,
  line_amount numeric
);

create table if not exists `retail-bigquery-project-webapp.raw_webapp.payments` (
  payment_id int64,
  order_id int64,
  payment_date date,
  payment_amount numeric,
  payment_method string,
  payment_status string
);

