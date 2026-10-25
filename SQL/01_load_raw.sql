
-- =====================================================
-- PROJECT: Telco Customer Churn Analysis
-- FILE: sql/01_load_raw.sql
-- PURPOSE: Create database, raw table, and verify data
-- DATABASE: MySQL
-- =====================================================

-- STEP 1: Create database
CREATE DATABASE IF NOT EXISTS telco_churn;

-- STEP 2: Select database
USE telco_churn;

-- STEP 3: Create raw table
-- All columns are TEXT to prevent import conversion errors.

CREATE TABLE IF NOT EXISTS raw_churn (
    customerID TEXT,
    gender TEXT,
    SeniorCitizen TEXT,
    Partner TEXT,
    Dependents TEXT,
    tenure TEXT,
    PhoneService TEXT,
    MultipleLines TEXT,
    InternetService TEXT,
    OnlineSecurity TEXT,
    OnlineBackup TEXT,
    DeviceProtection TEXT,
    TechSupport TEXT,
    StreamingTV TEXT,
    StreamingMovies TEXT,
    Contract TEXT,
    PaperlessBilling TEXT,
    PaymentMethod TEXT,
    MonthlyCharges TEXT,
    TotalCharges TEXT,
    Churn TEXT
);

-- STEP 4: Verify table structure
DESCRIBE raw_churn;

-- STEP 5: Count imported rows
SELECT COUNT(*) AS total_rows
FROM raw_churn;

-- STEP 6: Preview first 10 records
SELECT *
FROM raw_churn
LIMIT 10;

-- STEP 7: Check total and unique customer IDs
SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT customerID) AS unique_customers
FROM raw_churn;

-- STEP 8: Check churn distribution
SELECT
    Churn,
    COUNT(*) AS customer_count
FROM raw_churn
GROUP BY Churn
ORDER BY Churn;

-- STEP 9: Check missing or blank customer IDs
SELECT COUNT(*) AS missing_customer_ids
FROM raw_churn
WHERE customerID IS NULL
   OR TRIM(customerID) = '';

-- STEP 10: Check duplicate customer IDs
SELECT
    customerID,
    COUNT(*) AS occurrences
FROM raw_churn
GROUP BY customerID
HAVING COUNT(*) > 1;

-- STEP 11: Confirm all 21 columns exist
SELECT COUNT(*) AS total_columns
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'telco_churn'
  AND TABLE_NAME = 'raw_churn';
