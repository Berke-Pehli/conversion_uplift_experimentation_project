USE conversion_uplift_db;

-- Clear existing lookup data in dependency-safe order.
DELETE FROM fact_campaign_outcomes;
DELETE FROM fact_campaign_assignment;
DELETE FROM dim_customers;
DELETE FROM dim_campaign;
DELETE FROM dim_channel;
DELETE FROM dim_zip_code;

-- Insert zip code dimension values.
INSERT INTO dim_zip_code (zip_code_name)
VALUES
    ('Urban'),
    ('Rural'),
    ('Suburban');

-- Insert channel dimension values.
INSERT INTO dim_channel (channel_name)
VALUES
    ('Phone'),
    ('Web'),
    ('Multichannel');

-- Insert campaign dimension values.
INSERT INTO dim_campaign (segment, campaign_type, binary_treatment_flag)
VALUES
    ('Mens E-Mail', 'mens_email', 1),
    ('Womens E-Mail', 'womens_email', 1),
    ('No E-Mail', 'control', 0);