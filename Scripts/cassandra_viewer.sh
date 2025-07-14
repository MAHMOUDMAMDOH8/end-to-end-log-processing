#!/bin/bash

# Cassandra Data Viewer Script
# This script provides various ways to view data in Cassandra

echo "=== Cassandra Data Viewer ==="
echo ""

# Function to run CQL command
run_cql() {
    docker exec -it cassandra cqlsh -e "$1"
}

echo "1. Total number of records:"
run_cql "USE logs; SELECT COUNT(*) FROM ecomm_log;"
echo ""

echo "2. Latest 5 records (most recent first):"
run_cql "USE logs; SELECT timestamp, user_id, event_type, service, level FROM ecomm_log ORDER BY timestamp DESC LIMIT 5;"
echo ""

echo "3. Records by event type:"
run_cql "USE logs; SELECT event_type, COUNT(*) as count FROM ecomm_log GROUP BY event_type;"
echo ""

echo "4. Records by service:"
run_cql "USE logs; SELECT service, COUNT(*) as count FROM ecomm_log GROUP BY service;"
echo ""

echo "5. Records by level (INFO, ERROR, etc.):"
run_cql "USE logs; SELECT level, COUNT(*) as count FROM ecomm_log GROUP BY level;"
echo ""

echo "6. Sample of complete records (first 3):"
run_cql "USE logs; SELECT * FROM ecomm_log LIMIT 3;"
echo ""

echo "7. Records with errors (if any):"
run_cql "USE logs; SELECT timestamp, user_id, event_type, error_code, message FROM ecomm_log WHERE error_code IS NOT NULL;"
echo ""

echo "8. Records with payment information:"
run_cql "USE logs; SELECT timestamp, user_id, event_type, details_amount, details_payment_method FROM ecomm_log WHERE details_amount IS NOT NULL;"
echo ""

echo "=== Interactive Mode ==="
echo "To enter interactive CQL shell, run: docker exec -it cassandra cqlsh"
echo "Then use: USE logs;"
echo ""
echo "Useful CQL commands:"
echo "- DESCRIBE TABLE ecomm_log;  (show table structure)"
echo "- SELECT * FROM ecomm_log LIMIT 10;  (show 10 records)"
echo "- SELECT timestamp, user_id, event_type FROM ecomm_log WHERE user_id = 'user_247';  (filter by user)"
echo "- SELECT event_type, COUNT(*) FROM ecomm_log GROUP BY event_type;  (count by event type)" 