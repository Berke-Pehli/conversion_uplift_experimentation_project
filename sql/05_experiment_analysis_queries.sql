USE conversion_uplift_db;

-- =========================================================
-- 1. Base joined dataset for experiment analysis
-- =========================================================

SELECT
    c.customer_id,
    c.recency,
    c.history_segment,
    c.history,
    c.mens,
    c.womens,
    c.newbie,
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
LIMIT 20;


-- =========================================================
-- 2. Customer counts by campaign segment
-- =========================================================

SELECT
    cp.segment,
    cp.campaign_type,
    cp.binary_treatment_flag,
    COUNT(*) AS customer_count
FROM fact_campaign_assignment a
JOIN dim_campaign cp
    ON a.campaign_id = cp.campaign_id
GROUP BY cp.segment, cp.campaign_type, cp.binary_treatment_flag
ORDER BY customer_count DESC;


-- =========================================================
-- 3. Core KPI summary by campaign segment
-- =========================================================

SELECT
    cp.segment,
    COUNT(*) AS customer_count,
    ROUND(AVG(o.visit), 4) AS visit_rate,
    ROUND(AVG(o.conversion), 4) AS conversion_rate,
    ROUND(AVG(o.spend), 4) AS avg_spend_per_customer,
    ROUND(
        SUM(o.spend) / NULLIF(SUM(o.conversion), 0),
        4
    ) AS avg_spend_per_converter,
    ROUND(SUM(o.spend), 2) AS total_spend
FROM fact_campaign_assignment a
JOIN dim_campaign cp
    ON a.campaign_id = cp.campaign_id
JOIN fact_campaign_outcomes o
    ON a.customer_id = o.customer_id
GROUP BY cp.segment
ORDER BY cp.segment;


-- =========================================================
-- 4. Binary treatment vs control summary
-- =========================================================

SELECT
    cp.binary_treatment_flag,
    COUNT(*) AS customer_count,
    ROUND(AVG(o.visit), 4) AS visit_rate,
    ROUND(AVG(o.conversion), 4) AS conversion_rate,
    ROUND(AVG(o.spend), 4) AS avg_spend_per_customer,
    ROUND(SUM(o.spend), 2) AS total_spend
FROM fact_campaign_assignment a
JOIN dim_campaign cp
    ON a.campaign_id = cp.campaign_id
JOIN fact_campaign_outcomes o
    ON a.customer_id = o.customer_id
GROUP BY cp.binary_treatment_flag
ORDER BY cp.binary_treatment_flag;


-- =========================================================
-- 5. Uplift vs control by campaign segment
-- =========================================================

WITH segment_summary AS (
    SELECT
        cp.segment,
        ROUND(AVG(o.visit), 6) AS visit_rate,
        ROUND(AVG(o.conversion), 6) AS conversion_rate,
        ROUND(AVG(o.spend), 6) AS avg_spend_per_customer
    FROM fact_campaign_assignment a
    JOIN dim_campaign cp
        ON a.campaign_id = cp.campaign_id
    JOIN fact_campaign_outcomes o
        ON a.customer_id = o.customer_id
    GROUP BY cp.segment
),
control_baseline AS (
    SELECT
        visit_rate AS control_visit_rate,
        conversion_rate AS control_conversion_rate,
        avg_spend_per_customer AS control_avg_spend
    FROM segment_summary
    WHERE segment = 'No E-Mail'
)
SELECT
    s.segment,
    s.visit_rate,
    ROUND(s.visit_rate - c.control_visit_rate, 6) AS absolute_visit_uplift,
    ROUND(
        (s.visit_rate - c.control_visit_rate) / NULLIF(c.control_visit_rate, 0),
        6
    ) AS relative_visit_lift,
    s.conversion_rate,
    ROUND(s.conversion_rate - c.control_conversion_rate, 6) AS absolute_conversion_uplift,
    ROUND(
        (s.conversion_rate - c.control_conversion_rate) / NULLIF(c.control_conversion_rate, 0),
        6
    ) AS relative_conversion_lift,
    s.avg_spend_per_customer,
    ROUND(s.avg_spend_per_customer - c.control_avg_spend, 6) AS absolute_spend_uplift
FROM segment_summary s
CROSS JOIN control_baseline c
ORDER BY s.segment;


-- =========================================================
-- 6. Performance by channel and campaign
-- =========================================================

SELECT
    ch.channel_name,
    cp.segment,
    COUNT(*) AS customer_count,
    ROUND(AVG(o.visit), 4) AS visit_rate,
    ROUND(AVG(o.conversion), 4) AS conversion_rate,
    ROUND(AVG(o.spend), 4) AS avg_spend_per_customer
FROM dim_customers c
JOIN dim_channel ch
    ON c.channel_id = ch.channel_id
JOIN fact_campaign_assignment a
    ON c.customer_id = a.customer_id
JOIN dim_campaign cp
    ON a.campaign_id = cp.campaign_id
JOIN fact_campaign_outcomes o
    ON c.customer_id = o.customer_id
GROUP BY ch.channel_name, cp.segment
ORDER BY ch.channel_name, cp.segment;


-- =========================================================
-- 7. Performance by zip code and campaign
-- =========================================================

SELECT
    z.zip_code_name,
    cp.segment,
    COUNT(*) AS customer_count,
    ROUND(AVG(o.visit), 4) AS visit_rate,
    ROUND(AVG(o.conversion), 4) AS conversion_rate,
    ROUND(AVG(o.spend), 4) AS avg_spend_per_customer
FROM dim_customers c
JOIN dim_zip_code z
    ON c.zip_code_id = z.zip_code_id
JOIN fact_campaign_assignment a
    ON c.customer_id = a.customer_id
JOIN dim_campaign cp
    ON a.campaign_id = cp.campaign_id
JOIN fact_campaign_outcomes o
    ON c.customer_id = o.customer_id
GROUP BY z.zip_code_name, cp.segment
ORDER BY z.zip_code_name, cp.segment;


-- =========================================================
-- 8. New vs existing customer performance
-- =========================================================

SELECT
    c.newbie,
    cp.segment,
    COUNT(*) AS customer_count,
    ROUND(AVG(o.visit), 4) AS visit_rate,
    ROUND(AVG(o.conversion), 4) AS conversion_rate,
    ROUND(AVG(o.spend), 4) AS avg_spend_per_customer
FROM dim_customers c
JOIN fact_campaign_assignment a
    ON c.customer_id = a.customer_id
JOIN dim_campaign cp
    ON a.campaign_id = cp.campaign_id
JOIN fact_campaign_outcomes o
    ON c.customer_id = o.customer_id
GROUP BY c.newbie, cp.segment
ORDER BY c.newbie, cp.segment;


-- =========================================================
-- 9. Merchandise affinity by campaign
-- =========================================================

SELECT
    c.mens,
    c.womens,
    cp.segment,
    COUNT(*) AS customer_count,
    ROUND(AVG(o.visit), 4) AS visit_rate,
    ROUND(AVG(o.conversion), 4) AS conversion_rate,
    ROUND(AVG(o.spend), 4) AS avg_spend_per_customer
FROM dim_customers c
JOIN fact_campaign_assignment a
    ON c.customer_id = a.customer_id
JOIN dim_campaign cp
    ON a.campaign_id = cp.campaign_id
JOIN fact_campaign_outcomes o
    ON c.customer_id = o.customer_id
GROUP BY c.mens, c.womens, cp.segment
ORDER BY c.mens DESC, c.womens DESC, cp.segment;


-- =========================================================
-- 10. History segment performance
-- =========================================================

SELECT
    c.history_segment,
    cp.segment,
    COUNT(*) AS customer_count,
    ROUND(AVG(o.visit), 4) AS visit_rate,
    ROUND(AVG(o.conversion), 4) AS conversion_rate,
    ROUND(AVG(o.spend), 4) AS avg_spend_per_customer
FROM dim_customers c
JOIN fact_campaign_assignment a
    ON c.customer_id = a.customer_id
JOIN dim_campaign cp
    ON a.campaign_id = cp.campaign_id
JOIN fact_campaign_outcomes o
    ON c.customer_id = o.customer_id
GROUP BY c.history_segment, cp.segment
ORDER BY c.history_segment, cp.segment;


-- =========================================================
-- 11. Top-level business summary table
-- =========================================================

SELECT
    cp.segment,
    ch.channel_name,
    z.zip_code_name,
    COUNT(*) AS customer_count,
    ROUND(AVG(o.visit), 4) AS visit_rate,
    ROUND(AVG(o.conversion), 4) AS conversion_rate,
    ROUND(AVG(o.spend), 4) AS avg_spend_per_customer,
    ROUND(SUM(o.spend), 2) AS total_spend
FROM dim_customers c
JOIN dim_channel ch
    ON c.channel_id = ch.channel_id
JOIN dim_zip_code z
    ON c.zip_code_id = z.zip_code_id
JOIN fact_campaign_assignment a
    ON c.customer_id = a.customer_id
JOIN dim_campaign cp
    ON a.campaign_id = cp.campaign_id
JOIN fact_campaign_outcomes o
    ON c.customer_id = o.customer_id
GROUP BY cp.segment, ch.channel_name, z.zip_code_name
ORDER BY cp.segment, ch.channel_name, z.zip_code_name;