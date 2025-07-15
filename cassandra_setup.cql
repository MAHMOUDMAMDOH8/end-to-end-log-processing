-- Create keyspace for logs
CREATE KEYSPACE IF NOT EXISTS logs
WITH REPLICATION = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};

-- Use the logs keyspace
USE logs;

-- Create table for ecommerce logs
CREATE TABLE IF NOT EXISTS ecomm_log (
    timestamp text,
    user_id text,
    session_id text,
    product_id text,
    event_type text,
    level text,
    service text,
    session_duration int,
    device_type text,
    geo_country text,
    geo_city text,
    details_amount double,
    details_payment_method text,
    details_items text,
    details_order_id text,
    details_query text,
    details_results_count int,
    details_shipping_method text,
    details_delivery_estimate text,
    details_completed_at text,
    details_shipping_address text,
    error_code text,
    message text,
    error_at text,
    attempted_amount double,
    failed_at text,
    PRIMARY KEY (timestamp, user_id, session_id)
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS ON logs.ecomm_log (event_type);
CREATE INDEX IF NOT EXISTS ON logs.ecomm_log (user_id);
CREATE INDEX IF NOT EXISTS ON logs.ecomm_log (product_id);
CREATE INDEX IF NOT EXISTS ON logs.ecomm_log (level);
CREATE INDEX IF NOT EXISTS ON logs.ecomm_log (geo_country);

-- Insert a test record to verify the table structure
INSERT INTO logs.ecomm_log (
    timestamp, user_id, session_id, product_id, event_type, level, service,
    session_duration, device_type, geo_country, geo_city, details_amount,
    details_payment_method, details_items, error_code, message
) VALUES (
    '2025-07-14T19:22:08.639566Z', 'user_247', 'sess_62272', 'prod_00282',
    'order_complete', 'INFO', 'ecommerce-platform', 1430, 'tablet', 'IN', 'Delhi',
    798.6, 'credit_card', '[{"product_id":"prod_00282","quantity":2}]',
    null, null
);