-- ====================================================================
-- GRAFANA DASHBOARD QUERIES - CQL FORMAT
-- Extracted from grafana_monitoring_dashboard.json and world_map_dashboard.json
-- Compatible with Cassandra 3.x+ using the logs keyspace schema
-- ====================================================================

USE logs;

-- ====================================================================
-- SECTION 1: USER STATISTICS QUERIES
-- ====================================================================

-- Query 1: Total Users Count
SELECT COUNT(*) as total_users FROM logs.users;

-- Query 2: Users by Country (Egypt focus)
SELECT country, city, user_id, age 
FROM logs.users 
WHERE country = 'Egypt' 
ALLOW FILTERING;

-- Query 3: User Age Demographics
SELECT age, COUNT(*) as user_count 
FROM logs.users 
WHERE age > 18 AND age < 65 
ALLOW FILTERING;

-- ====================================================================
-- SECTION 2: PRODUCT ANALYTICS QUERIES
-- ====================================================================

-- Query 4: Total Products Count
SELECT COUNT(*) as total_products FROM logs.products;

-- Query 5: Fashion Products Count
SELECT COUNT(*) as fashion_products 
FROM logs.products 
WHERE category = 'Fashion' 
ALLOW FILTERING;

-- Query 6: Electronics Products Count
SELECT COUNT(*) as electronics_products 
FROM logs.products 
WHERE category = 'Electronics' 
ALLOW FILTERING;

-- Query 7: Beauty Products Count
SELECT COUNT(*) as beauty_products 
FROM logs.products 
WHERE category = 'Beauty' 
ALLOW FILTERING;

-- Query 8: Product Categories Analysis
SELECT category, COUNT(*) as product_count, AVG(price) as avg_price
FROM logs.products 
GROUP BY category 
ALLOW FILTERING;

-- Query 9: High-Value Products (>$500)
SELECT product_id, name, category, price 
FROM logs.products 
WHERE price > 500.0 
ALLOW FILTERING;

-- ====================================================================
-- SECTION 3: EVENT MONITORING QUERIES
-- ====================================================================

-- Query 10: Total Events Count
SELECT COUNT(*) as total_events FROM logs.ecomm_log;

-- Query 11: Purchase Events Count
SELECT COUNT(*) as purchase_events 
FROM logs.ecomm_log 
WHERE event_type = 'purchase' 
ALLOW FILTERING;

-- Query 12: Error Events Monitor
SELECT COUNT(*) as error_events 
FROM logs.ecomm_log 
WHERE level = 'ERROR' 
ALLOW FILTERING;

-- Query 13: Recent Activity (Last 24 hours)
SELECT COUNT(*) as recent_activity 
FROM logs.ecomm_log 
WHERE timestamp > '2024-12-20T12:00:00Z' 
ALLOW FILTERING;

-- Query 14: Today's Events
SELECT COUNT(*) as today_events 
FROM logs.ecomm_log 
WHERE timestamp > '2025-07-15' 
ALLOW FILTERING;

-- Query 15: Live Event Stream (Latest Events)
SELECT timestamp, event_type, user_id, geo_city, details_amount 
FROM logs.ecomm_log 
LIMIT 50;

-- Query 16: Event Types Breakdown
SELECT event_type, COUNT(*) as event_count 
FROM logs.ecomm_log 
GROUP BY event_type 
ALLOW FILTERING;

-- Query 17: Search Events
SELECT COUNT(*) as search_events 
FROM logs.ecomm_log 
WHERE event_type = 'search' 
ALLOW FILTERING;

-- Query 18: Order Completion Events
SELECT COUNT(*) as completed_orders 
FROM logs.ecomm_log 
WHERE event_type = 'order_complete' 
ALLOW FILTERING;

-- Query 19: Failed Orders Monitor
SELECT COUNT(*) as failed_orders 
FROM logs.ecomm_log 
WHERE event_type = 'order_failed' 
ALLOW FILTERING;

-- ====================================================================
-- SECTION 4: GEOGRAPHIC WORLD MAP QUERIES
-- ====================================================================

-- Query 20: Egypt Activity with Coordinates
SELECT 'Egypt' as country, 30.0444 as latitude, 31.2357 as longitude, COUNT(*) as value 
FROM logs.ecomm_log 
WHERE geo_country = 'Egypt' 
ALLOW FILTERING;

-- Query 21: USA Activity with Coordinates
SELECT 'USA' as country, 40.7128 as latitude, -74.0060 as longitude, COUNT(*) as value 
FROM logs.ecomm_log 
WHERE geo_country = 'US' 
ALLOW FILTERING;

-- Query 22: UK Activity with Coordinates
SELECT 'UK' as country, 51.5074 as latitude, -0.1278 as longitude, COUNT(*) as value 
FROM logs.ecomm_log 
WHERE geo_country = 'UK' 
ALLOW FILTERING;

-- Query 23: Germany Activity with Coordinates
SELECT 'Germany' as country, 52.5200 as latitude, 13.4050 as longitude, COUNT(*) as value 
FROM logs.ecomm_log 
WHERE geo_country = 'Germany' 
ALLOW FILTERING;

-- Query 24: Egypt Events Count
SELECT COUNT(*) as egypt_events 
FROM logs.ecomm_log 
WHERE geo_country = 'Egypt' 
ALLOW FILTERING;

-- Query 25: International Events (Non-Egypt)
SELECT COUNT(*) as international_events 
FROM logs.ecomm_log 
WHERE geo_country != 'Egypt' 
ALLOW FILTERING;

-- Query 26: Country Activity Summary
SELECT geo_country as country, COUNT(*) as events 
FROM logs.ecomm_log 
GROUP BY geo_country 
ALLOW FILTERING;

-- ====================================================================
-- SECTION 5: REVENUE AND TRANSACTION QUERIES
-- ====================================================================

-- Query 27: Total Revenue
SELECT SUM(details_amount) as total_revenue 
FROM logs.ecomm_log 
WHERE details_amount IS NOT NULL 
ALLOW FILTERING;

-- Query 28: Average Transaction Amount
SELECT AVG(details_amount) as avg_transaction 
FROM logs.ecomm_log 
WHERE details_amount IS NOT NULL 
ALLOW FILTERING;

-- Query 29: High-Value Transactions (>$500)
SELECT timestamp, user_id, details_amount, details_payment_method 
FROM logs.ecomm_log 
WHERE details_amount > 500.0 
ALLOW FILTERING;

-- Query 30: Payment Methods Distribution
SELECT details_payment_method, COUNT(*) as usage_count 
FROM logs.ecomm_log 
WHERE details_payment_method IS NOT NULL 
GROUP BY details_payment_method 
ALLOW FILTERING;

-- ====================================================================
-- SECTION 6: DEVICE AND SESSION ANALYTICS
-- ====================================================================

-- Query 31: Device Type Distribution
SELECT device_type, COUNT(*) as device_count 
FROM logs.ecomm_log 
WHERE device_type IS NOT NULL 
GROUP BY device_type 
ALLOW FILTERING;

-- Query 32: Mobile vs Desktop Activity
SELECT device_type, COUNT(*) as sessions 
FROM logs.ecomm_log 
WHERE device_type IN ('mobile', 'desktop') 
GROUP BY device_type 
ALLOW FILTERING;

-- Query 33: Session Duration Analysis
SELECT AVG(session_duration) as avg_session_duration 
FROM logs.ecomm_log 
WHERE session_duration IS NOT NULL 
ALLOW FILTERING;

-- ====================================================================
-- SECTION 7: ERROR MONITORING AND ALERTING
-- ====================================================================

-- Query 34: Error Codes Breakdown
SELECT error_code, COUNT(*) as error_count 
FROM logs.ecomm_log 
WHERE error_code IS NOT NULL 
GROUP BY error_code 
ALLOW FILTERING;

-- Query 35: Recent Errors (Last Hour)
SELECT timestamp, error_code, message, user_id 
FROM logs.ecomm_log 
WHERE level = 'ERROR' AND timestamp > '2024-12-20T16:00:00Z' 
ALLOW FILTERING;

-- Query 36: Failed Transactions by Amount
SELECT attempted_amount, COUNT(*) as failure_count 
FROM logs.ecomm_log 
WHERE attempted_amount IS NOT NULL 
GROUP BY attempted_amount 
ALLOW FILTERING;

-- ====================================================================
-- SECTION 8: CITY-LEVEL GEOGRAPHIC ANALYSIS
-- ====================================================================

-- Query 37: Egyptian Cities Activity
SELECT geo_city, COUNT(*) as city_events 
FROM logs.ecomm_log 
WHERE geo_country = 'Egypt' 
GROUP BY geo_city 
ALLOW FILTERING;

-- Query 38: Cairo Activity
SELECT COUNT(*) as cairo_events 
FROM logs.ecomm_log 
WHERE geo_city = 'Cairo' 
ALLOW FILTERING;

-- Query 39: Alexandria Activity
SELECT COUNT(*) as alexandria_events 
FROM logs.ecomm_log 
WHERE geo_city = 'Alexandria' 
ALLOW FILTERING;

-- Query 40: International Cities
SELECT geo_city, geo_country, COUNT(*) as events 
FROM logs.ecomm_log 
WHERE geo_country != 'Egypt' 
GROUP BY geo_city, geo_country 
ALLOW FILTERING;

-- ====================================================================
-- SECTION 9: TIME-BASED ANALYSIS
-- ====================================================================

-- Query 41: Events by Hour Pattern
SELECT timestamp, COUNT(*) as hourly_events 
FROM logs.ecomm_log 
WHERE timestamp > '2024-12-20T00:00:00Z' 
GROUP BY timestamp 
ALLOW FILTERING;

-- Query 42: Recent Purchase Activity
SELECT COUNT(*) as recent_purchases 
FROM logs.ecomm_log 
WHERE event_type = 'purchase' AND timestamp > '2024-12-20T12:00:00Z' 
ALLOW FILTERING;

-- ====================================================================
-- SECTION 10: BUSINESS INTELLIGENCE QUERIES
-- ====================================================================

-- Query 43: Top Products by Purchase Events
SELECT product_id, COUNT(*) as purchase_count 
FROM logs.ecomm_log 
WHERE event_type = 'purchase' AND product_id IS NOT NULL 
GROUP BY product_id 
ALLOW FILTERING;

-- Query 44: Active Users by Country
SELECT geo_country, COUNT(DISTINCT user_id) as active_users 
FROM logs.ecomm_log 
GROUP BY geo_country 
ALLOW FILTERING;

-- Query 45: Search Query Analysis
SELECT details_query, COUNT(*) as search_frequency 
FROM logs.ecomm_log 
WHERE event_type = 'search' AND details_query IS NOT NULL 
GROUP BY details_query 
ALLOW FILTERING;

-- ====================================================================
-- SECTION 11: OPERATIONAL MONITORING
-- ====================================================================

-- Query 46: Service Health Check
SELECT service, COUNT(*) as service_events 
FROM logs.ecomm_log 
WHERE service IS NOT NULL 
GROUP BY service 
ALLOW FILTERING;

-- Query 47: Order Processing Pipeline
SELECT details_shipping_method, COUNT(*) as shipping_count 
FROM logs.ecomm_log 
WHERE details_shipping_method IS NOT NULL 
GROUP BY details_shipping_method 
ALLOW FILTERING;

-- Query 48: Real-time Event Stream (Last 10 minutes)
SELECT timestamp, event_type, user_id, geo_city, details_amount, level 
FROM logs.ecomm_log 
WHERE timestamp > '2024-12-20T17:50:00Z' 
ALLOW FILTERING 
LIMIT 20;

