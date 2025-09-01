#!/bin/bash
# Ainflue Platform Development Server Runner
# Runs the application with hot-reload and development settings

set -e

# Load environment variables
export ENVIRONMENT=development
export DEBUG=true
export HOST=0.0.0.0
export PORT=8000

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "🚀 Starting Ainflue Development Server..."
echo "📍 Environment: $ENVIRONMENT"
echo "🌐 URL: http://$HOST:$PORT"
echo "📚 API Docs: http://$HOST:$PORT/docs"
echo "📖 ReDoc: http://$HOST:$PORT/redoc"
echo ""
echo "💡 Use Ctrl+C to stop the server"
echo ""

# Run with uvicorn for hot-reload
python -m uvicorn main:app \
    --host $HOST \
    --port $PORT \
    --reload \
    --reload-dir . \
    --reload-exclude "logs/*" \
    --reload-exclude "data/*" \
    --reload-exclude "storage/*" \
    --reload-exclude "backups/*" \
    --reload-exclude "__pycache__/*" \
    --reload-exclude "*.pyc" \
    --log-level debug \
    --access-log