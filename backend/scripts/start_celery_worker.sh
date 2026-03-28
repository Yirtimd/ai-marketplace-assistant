#!/bin/bash
# Celery worker startup script

set -euo pipefail

# Resolve project directories relative to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Set Python path
export PYTHONPATH="${PYTHONPATH:-}:${BACKEND_DIR}"

# Start Celery worker
echo "Starting Celery worker..."
"${BACKEND_DIR}/venv/bin/celery" -A celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --max-tasks-per-child=1000 \
    --logfile="${BACKEND_DIR}/logs/celery_worker.log"
