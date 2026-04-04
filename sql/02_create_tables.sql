USE conversion_uplift_db;

DROP TABLE IF EXISTS fact_campaign_outcomes;
DROP TABLE IF EXISTS fact_campaign_assignment;
DROP TABLE IF EXISTS dim_customers;
DROP TABLE IF EXISTS dim_campaign;
DROP TABLE IF EXISTS dim_channel;
DROP TABLE IF EXISTS dim_zip_code;

CREATE TABLE dim_zip_code (
    zip_code_id INT PRIMARY KEY AUTO_INCREMENT,
    zip_code_name VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE dim_channel (
    channel_id INT PRIMARY KEY AUTO_INCREMENT,
    channel_name VARCHAR(30) NOT NULL UNIQUE
);

CREATE TABLE dim_campaign (
    campaign_id INT PRIMARY KEY AUTO_INCREMENT,
    segment VARCHAR(30) NOT NULL UNIQUE,
    campaign_type VARCHAR(30) NOT NULL,
    binary_treatment_flag TINYINT NOT NULL
);

CREATE TABLE dim_customers (
    customer_id INT PRIMARY KEY,
    recency INT NOT NULL,
    history_segment VARCHAR(50) NOT NULL,
    history DECIMAL(10, 2) NOT NULL,
    mens TINYINT NOT NULL,
    womens TINYINT NOT NULL,
    newbie TINYINT NOT NULL,
    zip_code_id INT NOT NULL,
    channel_id INT NOT NULL,
    CONSTRAINT fk_customers_zip_code
        FOREIGN KEY (zip_code_id)
        REFERENCES dim_zip_code(zip_code_id),
    CONSTRAINT fk_customers_channel
        FOREIGN KEY (channel_id)
        REFERENCES dim_channel(channel_id)
);

CREATE TABLE fact_campaign_assignment (
    customer_id INT PRIMARY KEY,
    campaign_id INT NOT NULL,
    CONSTRAINT fk_assignment_customer
        FOREIGN KEY (customer_id)
        REFERENCES dim_customers(customer_id),
    CONSTRAINT fk_assignment_campaign
        FOREIGN KEY (campaign_id)
        REFERENCES dim_campaign(campaign_id)
);

CREATE TABLE fact_campaign_outcomes (
    customer_id INT PRIMARY KEY,
    visit TINYINT NOT NULL,
    conversion TINYINT NOT NULL,
    spend DECIMAL(10, 2) NOT NULL,
    CONSTRAINT fk_outcomes_customer
        FOREIGN KEY (customer_id)
        REFERENCES dim_customers(customer_id)
);