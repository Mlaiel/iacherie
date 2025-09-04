#!/bin/bash
# Generated startup test script for docker-compose.yml
# Run this to test service startup

set -e

echo "🚀 Testing docker-compose.yml service startup..."

# Clean up any existing containers
docker compose -f docker-compose.yml down --remove-orphans || true

# Pull latest images
echo "📥 Pulling images..."
docker compose -f docker-compose.yml pull --ignore-pull-failures

# Start services
echo "🔧 Starting services..."
docker compose -f docker-compose.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🩺 Checking service health..."

# Check ainflue-app
if curl -f -s http://localhost:8000/health > /dev/null; then
    echo "✅ ainflue-app is healthy"
else
    echo "❌ ainflue-app is not responding"
fi

# Check nginx
if curl -f -s http://localhost:80/health > /dev/null; then
    echo "✅ nginx is healthy"
else
    echo "❌ nginx is not responding"
fi

# Check prometheus
if curl -f -s http://localhost:9090/-/healthy > /dev/null; then
    echo "✅ prometheus is healthy"
else
    echo "❌ prometheus is not responding"
fi

# Check grafana
if curl -f -s http://localhost:3000/api/health > /dev/null; then
    echo "✅ grafana is healthy"
else
    echo "❌ grafana is not responding"
fi

echo "📊 Service status:"
docker compose -f docker-compose.yml ps

echo "🎉 Startup test completed!"
