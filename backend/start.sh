#!/bin/bash

# AI Marketplace Assistant - Backend Startup Script

set -e

echo "🚀 Starting AI Marketplace Assistant Backend"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
if [ ! -f "venv/.requirements_installed" ]; then
    echo "📚 Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    touch venv/.requirements_installed
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your actual configuration!"
    echo ""
fi

# Check if Docker services are running
echo "🐳 Checking Docker services..."
if ! docker ps | grep -q ai_marketplace_postgres; then
    echo "⚠️  PostgreSQL container not running. Starting Docker services..."
    docker-compose up -d
    echo "⏳ Waiting for services to be ready..."
    sleep 5
fi

# Create logs directory
mkdir -p logs

echo ""
echo "✅ Environment ready!"
echo ""
echo "🌐 Starting FastAPI server..."
echo "📍 API will be available at: http://localhost:8000"
echo "📖 API docs will be available at: http://localhost:8000/docs"
echo ""

# Start the server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
