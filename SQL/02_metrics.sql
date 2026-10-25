USE telcochurn_db;

-- 1. Overall churn rate: answers what percentage of all customers churned.
SELECT
    COUNT(*) AS total_customers,
    SUM(churned = 1) AS churned_customers,
    ROUND(AVG(churned) * 100, 2) AS churn_rate_percent
FROM clean_churn;

-- 2. Churn by contract: compares customer counts and churn rates across contract types.
SELECT
    contract,
    COUNT(*) AS total_customers,
    SUM(churned = 1) AS churned_customers,
    ROUND(AVG(churned) * 100, 2) AS churn_rate_percent
FROM clean_churn
GROUP BY contract
ORDER BY churn_rate_percent DESC;

-- 3. Churn by internet service: compares churn rates for each internet service category.
SELECT
    internet_service,
    COUNT(*) AS total_customers,
    SUM(churned = 1) AS churned_customers,
    ROUND(AVG(churned) * 100, 2) AS churn_rate_percent
FROM clean_churn
GROUP BY internet_service
ORDER BY churn_rate_percent DESC;

-- 4. Churn by payment method: identifies payment methods associated with higher churn rates.
SELECT
    payment_method,
    COUNT(*) AS total_customers,
    SUM(churned = 1) AS churned_customers,
    ROUND(AVG(churned) * 100, 2) AS churn_rate_percent
FROM clean_churn
GROUP BY payment_method
ORDER BY churn_rate_percent DESC;

-- 5. Churn by tenure bucket: compares churn rates for customers grouped by months with the company.
SELECT
    CASE
        WHEN tenure BETWEEN 0 AND 6 THEN '0-6 months'
        WHEN tenure BETWEEN 7 AND 12 THEN '7-12 months'
        WHEN tenure BETWEEN 13 AND 24 THEN '13-24 months'
        WHEN tenure >= 25 THEN '25+ months'
        ELSE 'Unknown'
    END AS tenure_bucket,
    COUNT(*) AS total_customers,
    SUM(churned = 1) AS churned_customers,
    ROUND(AVG(churned) * 100, 2) AS churn_rate_percent
FROM clean_churn
GROUP BY tenure_bucket
ORDER BY FIELD(tenure_bucket, '0-6 months', '7-12 months', '13-24 months', '25+ months', 'Unknown');

-- 6. Revenue lost to churn: estimates monthly recurring charges associated with customers who churned.
SELECT
    ROUND(SUM(monthly_charges), 2) AS monthly_revenue_lost,
    COUNT(*) AS churned_customers,
    ROUND(AVG(monthly_charges), 2) AS average_monthly_charge_per_churned_customer
FROM clean_churn
WHERE churned = 1;
