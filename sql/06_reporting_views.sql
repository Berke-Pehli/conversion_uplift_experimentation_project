USE conversion_uplift_db;

-- =========================================================
-- 1. Customer-level joined reporting view
-- =========================================================

DROP VIEW IF EXISTS vw_customer_experiment_detail;

CREATE VIEW vw_customer_experiment_detail AS
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
    ON c.customer_id = o.customer_id;


-- =========================================================
-- 2. Campaign summary reporting view
-- =========================================================

DROP VIEW IF EXISTS vw_campaign_summary;

CREATE VIEW vw_campaign_summary AS
SELECT
    segment,
    campaign_type,
    binary_treatment_flag,
    COUNT(*) AS customer_count,
    ROUND(AVG(visit), 4) AS visit_rate,
    ROUND(AVG(conversion), 4) AS conversion_rate,
    ROUND(AVG(spend), 4) AS avg_spend_per_customer,
    ROUND(SUM(spend), 2) AS total_spend,
    ROUND(
        SUM(spend) / NULLIF(SUM(conversion), 0),
        4
    ) AS avg_spend_per_converter
FROM vw_customer_experiment_detail
GROUP BY
    segment,
    campaign_type,
    binary_treatment_flag;


-- =========================================================
-- 3. Binary treatment vs control reporting view
-- =========================================================

DROP VIEW IF EXISTS vw_treatment_control_summary;

CREATE VIEW vw_treatment_control_summary AS
SELECT
    binary_treatment_flag,
    COUNT(*) AS customer_count,
    ROUND(AVG(visit), 4) AS visit_rate,
    ROUND(AVG(conversion), 4) AS conversion_rate,
    ROUND(AVG(spend), 4) AS avg_spend_per_customer,
    ROUND(SUM(spend), 2) AS total_spend
FROM vw_customer_experiment_detail
GROUP BY binary_treatment_flag;


-- =========================================================
-- 4. Segment uplift vs control view
-- =========================================================

DROP VIEW IF EXISTS vw_segment_uplift_summary;

CREATE VIEW vw_segment_uplift_summary AS
WITH segment_summary AS (
    SELECT
        segment,
        AVG(visit) AS visit_rate,
        AVG(conversion) AS conversion_rate,
        AVG(spend) AS avg_spend_per_customer
    FROM vw_customer_experiment_detail
    GROUP BY segment
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
    ROUND(s.visit_rate, 6) AS visit_rate,
    ROUND(s.visit_rate - c.control_visit_rate, 6) AS absolute_visit_uplift,
    ROUND(
        (s.visit_rate - c.control_visit_rate) / NULLIF(c.control_visit_rate, 0),
        6
    ) AS relative_visit_lift,
    ROUND(s.conversion_rate, 6) AS conversion_rate,
    ROUND(s.conversion_rate - c.control_conversion_rate, 6) AS absolute_conversion_uplift,
    ROUND(
        (s.conversion_rate - c.control_conversion_rate) / NULLIF(c.control_conversion_rate, 0),
        6
    ) AS relative_conversion_lift,
    ROUND(s.avg_spend_per_customer, 6) AS avg_spend_per_customer,
    ROUND(s.avg_spend_per_customer - c.control_avg_spend, 6) AS absolute_spend_uplift
FROM segment_summary s
CROSS JOIN control_baseline c;


-- =========================================================
-- 5. Channel-level campaign summary view
-- =========================================================

DROP VIEW IF EXISTS vw_channel_campaign_summary;

CREATE VIEW vw_channel_campaign_summary AS
SELECT
    channel_name,
    segment,
    campaign_type,
    COUNT(*) AS customer_count,
    ROUND(AVG(visit), 4) AS visit_rate,
    ROUND(AVG(conversion), 4) AS conversion_rate,
    ROUND(AVG(spend), 4) AS avg_spend_per_customer,
    ROUND(SUM(spend), 2) AS total_spend
FROM vw_customer_experiment_detail
GROUP BY
    channel_name,
    segment,
    campaign_type;


-- =========================================================
-- 6. Zip-code-level campaign summary view
-- =========================================================

DROP VIEW IF EXISTS vw_zip_campaign_summary;

CREATE VIEW vw_zip_campaign_summary AS
SELECT
    zip_code_name,
    segment,
    campaign_type,
    COUNT(*) AS customer_count,
    ROUND(AVG(visit), 4) AS visit_rate,
    ROUND(AVG(conversion), 4) AS conversion_rate,
    ROUND(AVG(spend), 4) AS avg_spend_per_customer,
    ROUND(SUM(spend), 2) AS total_spend
FROM vw_customer_experiment_detail
GROUP BY
    zip_code_name,
    segment,
    campaign_type;


-- =========================================================
-- 7. New-vs-existing customer summary view
-- =========================================================

DROP VIEW IF EXISTS vw_newbie_campaign_summary;

CREATE VIEW vw_newbie_campaign_summary AS
SELECT
    newbie,
    segment,
    campaign_type,
    COUNT(*) AS customer_count,
    ROUND(AVG(visit), 4) AS visit_rate,
    ROUND(AVG(conversion), 4) AS conversion_rate,
    ROUND(AVG(spend), 4) AS avg_spend_per_customer,
    ROUND(SUM(spend), 2) AS total_spend
FROM vw_customer_experiment_detail
GROUP BY
    newbie,
    segment,
    campaign_type;


-- =========================================================
-- 8. History-segment campaign summary view
-- =========================================================

DROP VIEW IF EXISTS vw_history_segment_campaign_summary;

CREATE VIEW vw_history_segment_campaign_summary AS
SELECT
    history_segment,
    segment,
    campaign_type,
    COUNT(*) AS customer_count,
    ROUND(AVG(visit), 4) AS visit_rate,
    ROUND(AVG(conversion), 4) AS conversion_rate,
    ROUND(AVG(spend), 4) AS avg_spend_per_customer,
    ROUND(SUM(spend), 2) AS total_spend
FROM vw_customer_experiment_detail
GROUP BY
    history_segment,
    segment,
    campaign_type;