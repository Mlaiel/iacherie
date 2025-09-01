#!/bin/bash
# Ainflue Platform Performance Profiler
# Profiles the application for performance analysis

set -e

echo "📈 Starting Ainflue Performance Profiling..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Create profiles directory
mkdir -p profiles

# Set environment
export ENVIRONMENT=development
export DEBUG=false

echo "🔍 Running CPU profiling with py-spy..."
# Start the application in background
python main.py &
APP_PID=$!

# Wait for app to start
sleep 5

# Profile for 30 seconds
py-spy record -o profiles/cpu_profile.svg -d 30 -p $APP_PID

# Stop the application
kill $APP_PID

echo ""
echo "🧠 Running memory profiling..."
# Memory profiling
python -m memory_profiler main.py > profiles/memory_profile.txt

echo ""
echo "⚡ Running line profiling..."
# Line profiling (requires @profile decorators)
if command -v kernprof &> /dev/null; then
    kernprof -l -v main.py > profiles/line_profile.txt 2>&1 || echo "Line profiling requires @profile decorators"
fi

echo ""
echo "📊 Profiling completed!"
echo "🖥️  CPU Profile: profiles/cpu_profile.svg"
echo "🧠 Memory Profile: profiles/memory_profile.txt"
echo "⚡ Line Profile: profiles/line_profile.txt"
echo ""
echo "💡 Open cpu_profile.svg in a browser to view the flame graph"