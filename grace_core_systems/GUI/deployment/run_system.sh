#!/bin/bash

# Grace System Boot Script
# Loads environment, verifies dependencies, and starts Grace Core.

echo "🚀 Launching Grace System..."

# Load environment
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "⚠️  .env file not found. Falling back to .env.example"
    export $(grep -v '^#' .env.example | xargs)
fi

# Start Redis (dockerized)
echo "🔧 Starting Redis container..."
docker-compose up -d redis

# Start Grace backend services
echo "🧠 Starting Grace FastAPI backend..."
uvicorn dashboard_api:app --reload --host 0.0.0.0 --port 8000

# Optional future extension:
# echo "📡 Starting WebSocket Router..."
# python websocket_router.py 
chmod +x GUI/deployment/run_system.sh