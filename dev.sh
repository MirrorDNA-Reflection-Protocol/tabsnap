#!/bin/bash
# TabSnap local dev — starts API + web frontend
# Usage: ./dev.sh

set -e
cd "$(dirname "$0")"

echo "=== TabSnap Local Dev ==="

# Activate venv
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -q -r services/api/requirements.txt -r services/worker/requirements.txt
fi

# Ensure data dirs exist
mkdir -p data/uploads data/outputs

# Start API server in background
echo "Starting API on :8000..."
cd services/api
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!
cd ../..

# Start Next.js dev in background
echo "Starting web on :3000..."
cd apps/web
npm run dev &
WEB_PID=$!
cd ../..

echo ""
echo "TabSnap running:"
echo "  Frontend: http://localhost:3000"
echo "  API:      http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop."

trap "kill $API_PID $WEB_PID 2>/dev/null; exit" INT TERM
wait
