-- Create database
CREATE DATABASE sales;

-- Connect to the sales database
\connect sales

-- Create schema for raw data
CREATE SCHEMA IF NOT EXISTS raw__sales;

-- Create table
CREATE TABLE IF NOT EXISTS raw__sales.fct_sales (
    SaleID INT PRIMARY KEY,
    ProductID TEXT,
    ProductName TEXT,
    Brand TEXT,
    Category TEXT,
    RetailerID INT,
    RetailerName TEXT,
    Channel TEXT,
    Location TEXT,
    Quantity TEXT,
    Price TEXT,
    Date DATE,
    _etl_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sourceFileName TEXT
);

-- Create index
CREATE UNIQUE INDEX IF NOT EXISTS idx_sale_id ON raw__sales.fct_sales (SaleID);
