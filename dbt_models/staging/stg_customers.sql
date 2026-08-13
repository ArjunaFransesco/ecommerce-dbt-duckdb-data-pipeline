-- Staging Customers: Type casting, trimming, and schema normalization
SELECT
    TRIM(customer_id) AS customer_id,
    TRIM(first_name) AS first_name,
    TRIM(last_name) AS last_name,
    CONCAT(TRIM(first_name), ' ', TRIM(last_name)) AS full_name,
    LOWER(TRIM(email)) AS email,
    TRIM(city) AS city,
    TRIM(country) AS country,
    CAST(signup_timestamp AS TIMESTAMP) AS signup_at,
    CAST(signup_timestamp AS DATE) AS signup_date,
    TRIM(device_preference) AS device_preference
FROM raw_customers;
