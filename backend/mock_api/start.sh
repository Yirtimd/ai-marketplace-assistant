#!/bin/bash

# Wildberries Mock API - Startup Script

set -e

echo "🚀 Starting Wildberries Mock API Server"
echo ""

# Check if virtual environment exists
if [ ! -d "../venv" ]; then
    echo "⚠️  Virtual environment not found. Please run setup from backend/ directory first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source ../venv/bin/activate

echo "✅ Environment ready!"
echo ""
echo "🌐 Starting Mock API server..."
echo "📍 API will be available at: http://localhost:8001"
echo "📖 API docs will be available at: http://localhost:8001/docs"
echo ""
echo "🔑 Test API Key: test-api-key-12345"
echo ""

# Start the server (run from parent directory as Python module)
cd ..
python -m uvicorn mock_api.main:app --reload --host 0.0.0.0 --port 8001
