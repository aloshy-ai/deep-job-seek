#!/bin/bash

set -e

# Wait for Qdrant to be ready
# QDRANT_HOST and QDRANT_PORT are set as environment variables in docker-compose.yml
QDRANT_HEALTH_URL="http://${QDRANT_HOST}:${QDRANT_PORT}/healthz"

echo "Waiting for Qdrant at ${QDRANT_HEALTH_URL}..."
until curl -s ${QDRANT_HEALTH_URL} | head -n 1 | grep -q "200 OK"; do
  echo -n "."
  sleep 1
done
echo "\nQdrant is up!"

# Run the data population script
echo "Running data population script..."
python scripts/populate_test_data.py

# Start the main application
echo "Starting main application..."
exec python main.py

