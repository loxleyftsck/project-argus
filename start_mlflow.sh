#!/bin/bash
# Start MLflow UI Server
# Usage: ./start_mlflow.sh

echo "Starting MLflow UI..."
echo "Access at: http://localhost:5000"
echo "Press Ctrl+C to stop"

mlflow ui --port 5000 --host 0.0.0.0
