-- Create keyspace for logs
CREATE KEYSPACE IF NOT EXISTS logs
WITH REPLICATION = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};

-- Use the logs keyspace
USE logs;

-- Create table for users
CREATE TABLE IF NOT EXISTS users (
    user_id text PRIMARY KEY,
    username text,
    email text,
    full_name text,
    first_name text,
    last_name text,
    sex text,
    age int,
    country text,
    city text,
    signup_date text
);

-- Create table for products
CREATE TABLE IF NOT EXISTS products (
    product_id text PRIMARY KEY,
    name text,
    category text,
    subcategory text,
    price double,
    brand text,
    description text,
    stock int,
    rating double,
    date_added text,
    weight text
);

-- Create table for ecommerce logs (updated with relationships)
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

-- Create indexes for users
CREATE INDEX IF NOT EXISTS ON logs.users (country);
CREATE INDEX IF NOT EXISTS ON logs.users (city);
CREATE INDEX IF NOT EXISTS ON logs.users (age);

-- Create indexes for products
CREATE INDEX IF NOT EXISTS ON logs.products (category);
CREATE INDEX IF NOT EXISTS ON logs.products (brand);
CREATE INDEX IF NOT EXISTS ON logs.products (price);

-- Note: Materialized views are disabled in this Cassandra configuration
-- You can create additional tables manually if needed for analytics

-- Insert sample test records
INSERT INTO logs.users (user_id, username, email, full_name, first_name, last_name, sex, age, country, city, signup_date)
VALUES ('user_1', 'test_user', 'test@example.com', 'Test User', 'Test', 'User', 'male', 25, 'US', 'New York', '2024-01-01');

INSERT INTO logs.products (product_id, name, category, subcategory, price, brand, description, stock, rating, date_added, weight)
VALUES ('prod_00001', 'Test Product', 'Electronics', 'Phones', 999.99, 'TestBrand', 'A test product', 100, 4.5, '2024-01-01', '200g');

INSERT INTO logs.ecomm_log (
    timestamp, user_id, session_id, product_id, event_type, level, service,
    session_duration, device_type, geo_country, geo_city, details_amount,
    details_payment_method, details_items, error_code, message
) VALUES (
    '2025-07-15T17:00:00.000Z', 'user_1', 'sess_12345', 'prod_00001',
    'purchase', 'INFO', 'ecommerce-platform', 1200, 'mobile', 'US', 'New York',
    999.99, 'credit_card', '[{"product_id":"prod_00001","quantity":1}]',
    null, null
);