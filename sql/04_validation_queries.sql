USE conversion_uplift_db;

-- =========================================================
-- 1. Row count checks
-- =========================================================

SELECT 'dim_zip_code' AS table_name, COUNT(*) AS row_count
FROM dim_zip_code
UNION ALL
SELECT 'dim_channel' AS table_name, COUNT(*) AS row_count
FROM dim_channel
UNION ALL
SELECT 'dim_campaign' AS table_name, COUNT(*) AS row_count
FROM dim_campaign
UNION ALL
SELECT 'dim_customers' AS table_name, COUNT(*) AS row_count
FROM dim_customers
UNION ALL
SELECT 'fact_campaign_assignment' AS table_name, COUNT(*) AS row_count
FROM fact_campaign_assignment
UNION ALL
SELECT 'fact_campaign_outcomes' AS table_name, COUNT(*) AS row_count
FROM fact_campaign_outcomes;


-- =========================================================
-- 2. Duplicate primary key checks
-- =========================================================

SELECT customer_id, COUNT(*) AS duplicate_count
FROM dim_customers
GROUP BY customer_id
HAVING COUNT(*) > 1;

SELECT customer_id, COUNT(*) AS duplicate_count
FROM fact_campaign_assignment
GROUP BY customer_id
HAVING COUNT(*) > 1;

SELECT customer_id, COUNT(*) AS duplicate_count
FROM fact_campaign_outcomes
GROUP BY customer_id
HAVING COUNT(*) > 1;


-- =========================================================
-- 3. Null checks in critical columns
-- =========================================================

SELECT
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS null_customer_id,
    SUM(CASE WHEN recency IS NULL THEN 1 ELSE 0 END) AS null_recency,
    SUM(CASE WHEN history_segment IS NULL THEN 1 ELSE 0 END) AS null_history_segment,
    SUM(CASE WHEN history IS NULL THEN 1 ELSE 0 END) AS null_history,
    SUM(CASE WHEN zip_code_id IS NULL THEN 1 ELSE 0 END) AS null_zip_code_id,
    SUM(CASE WHEN channel_id IS NULL THEN 1 ELSE 0 END) AS null_channel_id
FROM dim_customers;

SELECT
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS null_customer_id,
    SUM(CASE WHEN campaign_id IS NULL THEN 1 ELSE 0 END) AS null_campaign_id
FROM fact_campaign_assignment;

SELECT
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS null_customer_id,
    SUM(CASE WHEN visit IS NULL THEN 1 ELSE 0 END) AS null_visit,
    SUM(CASE WHEN conversion IS NULL THEN 1 ELSE 0 END) AS null_conversion,
    SUM(CASE WHEN spend IS NULL THEN 1 ELSE 0 END) AS null_spend
FROM fact_campaign_outcomes;


-- =========================================================
-- 4. Foreign key join integrity checks
-- =========================================================

SELECT COUNT(*) AS missing_customer_in_assignment
FROM fact_campaign_assignment a
LEFT JOIN dim_customers c
    ON a.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

SELECT COUNT(*) AS missing_customer_in_outcomes
FROM fact_campaign_outcomes o
LEFT JOIN dim_customers c
    ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

SELECT COUNT(*) AS missing_campaign_lookup
FROM fact_campaign_assignment a
LEFT JOIN dim_campaign cp
    ON a.campaign_id = cp.campaign_id
WHERE cp.campaign_id IS NULL;

SELECT COUNT(*) AS missing_zip_lookup
FROM dim_customers c
LEFT JOIN dim_zip_code z
    ON c.zip_code_id = z.zip_code_id
WHERE z.zip_code_id IS NULL;

SELECT COUNT(*) AS missing_channel_lookup
FROM dim_customers c
LEFT JOIN dim_channel ch
    ON c.channel_id = ch.channel_id
WHERE ch.channel_id IS NULL;


-- =========================================================
-- 5. Binary value checks
-- =========================================================

SELECT mens, COUNT(*) AS row_count
FROM dim_customers
GROUP BY mens
ORDER BY mens;

SELECT womens, COUNT(*) AS row_count
FROM dim_customers
GROUP BY womens
ORDER BY womens;

SELECT newbie, COUNT(*) AS row_count
FROM dim_customers
GROUP BY newbie
ORDER BY newbie;

SELECT binary_treatment_flag, COUNT(*) AS row_count
FROM dim_campaign
GROUP BY binary_treatment_flag
ORDER BY binary_treatment_flag;

SELECT visit, COUNT(*) AS row_count
FROM fact_campaign_outcomes
GROUP BY visit
ORDER BY visit;

SELECT conversion, COUNT(*) AS row_count
FROM fact_campaign_outcomes
GROUP BY conversion
ORDER BY conversion;


-- =========================================================
-- 6. Outcome sanity checks
-- =========================================================

SELECT
    MIN(spend) AS min_spend,
    MAX(spend) AS max_spend,
    AVG(spend) AS avg_spend
FROM fact_campaign_outcomes;

SELECT
    MIN(history) AS min_history,
    MAX(history) AS max_history,
    AVG(history) AS avg_history
FROM dim_customers;

SELECT
    MIN(recency) AS min_recency,
    MAX(recency) AS max_recency,
    AVG(recency) AS avg_recency
FROM dim_customers;


-- =========================================================
-- 7. Dimension distribution checks
-- =========================================================

SELECT z.zip_code_name, COUNT(*) AS customer_count
FROM dim_customers c
JOIN dim_zip_code z
    ON c.zip_code_id = z.zip_code_id
GROUP BY z.zip_code_name
ORDER BY customer_count DESC;

SELECT ch.channel_name, COUNT(*) AS customer_count
FROM dim_customers c
JOIN dim_channel ch
    ON c.channel_id = ch.channel_id
GROUP BY ch.channel_name
ORDER BY customer_count DESC;

SELECT cp.segment, cp.campaign_type, cp.binary_treatment_flag, COUNT(*) AS customer_count
FROM fact_campaign_assignment a
JOIN dim_campaign cp
    ON a.campaign_id = cp.campaign_id
GROUP BY cp.segment, cp.campaign_type, cp.binary_treatment_flag
ORDER BY customer_count DESC;


-- =========================================================
-- 8. Full join validation sample
-- =========================================================

SELECT
    c.customer_id,
    c.recency,
    c.history_segment,
    c.history,
    z.zip_code_name,
    ch.channel_name,
    cp.segment,
    cp.campaign_type,
    cp.binary_treatment_flag,
    o.visit,
    o.conversion,
    o.spend
FROM dim_customers c
JOIN dim_zip_code z
    ON c.zip_code_id = z.zip_code_id
JOIN dim_channel ch
    ON c.channel_id = ch.channel_id
JOIN fact_campaign_assignment a
    ON c.customer_id = a.customer_id
JOIN dim_campaign cp
    ON a.campaign_id = cp.campaign_id
JOIN fact_campaign_outcomes o
    ON c.customer_id = o.customer_id
LIMIT 10;