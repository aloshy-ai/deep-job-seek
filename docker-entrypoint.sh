#!/bin/bash

set -e

# Run the data population script
echo "Running data population script..."
python scripts/populate_test_data.py

# Start the main application
echo "Starting main application..."
exec python main.py
