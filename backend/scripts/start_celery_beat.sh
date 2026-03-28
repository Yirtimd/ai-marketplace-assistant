#!/bin/bash
# Celery beat startup script

# Set Python path
export PYTHONPATH="${PYTHONPATH}:/Users/nomads_dm/Desktop/sl_AI_ve/ai-marketplace-assistant/backend"

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Start Celery beat scheduler
echo "Starting Celery beat scheduler..."
celery -A celery_app beat \
    --loglevel=info \
    --logfile=logs/celery_beat.log
