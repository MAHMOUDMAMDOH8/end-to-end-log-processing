#!/bin/bash

echo "Setting up Cassandra database and table..."

# Execute the CQL file
docker exec -i cassandra cqlsh < cassandra_setup.cql

echo "Cassandra setup completed!"
echo "Keyspace: logs"
echo "Table: ecomm_log"

# Verify the setup
echo ""
echo "Verifying setup..."
docker exec cassandra cqlsh -e "DESCRIBE KEYSPACES;"
echo ""
docker exec cassandra cqlsh -e "USE logs; DESCRIBE TABLES;"
echo ""
docker exec cassandra cqlsh -e "USE logs; SELECT COUNT(*) FROM ecomm_log;" 