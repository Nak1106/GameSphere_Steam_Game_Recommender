#!/bin/bash

# GameSphere Steam Recommender - MLflow UI Helper Script
# Starts MLflow UI with local SQLite backend and file-based artifact store

echo "🚀 Starting MLflow UI for GameSphere..."
echo "MLflow UI will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop"

# Start MLflow UI with local configuration
mlflow ui \
    --backend-store-uri sqlite:///mlflow.db \
    --default-artifact-root ./mlruns \
    --host 0.0.0.0 \
    --port 5000
