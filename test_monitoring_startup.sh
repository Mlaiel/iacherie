#!/bin/bash
# Generated startup test script for docker-compose.monitoring.yml
# Run this to test service startup

set -e

echo "🚀 Testing docker-compose.monitoring.yml service startup..."

# Clean up any existing containers
docker compose -f docker-compose.monitoring.yml down --remove-orphans || true

# Pull latest images
echo "📥 Pulling images..."
docker compose -f docker-compose.monitoring.yml pull --ignore-pull-failures

# Start services
echo "🔧 Starting services..."
docker compose -f docker-compose.monitoring.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🩺 Checking service health..."

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

# Check elasticsearch
if curl -f -s http://localhost:9200/_cluster/health > /dev/null; then
    echo "✅ elasticsearch is healthy"
else
    echo "❌ elasticsearch is not responding"
fi

# Check alertmanager
if curl -f -s http://localhost:9093/-/healthy > /dev/null; then
    echo "✅ alertmanager is healthy"
else
    echo "❌ alertmanager is not responding"
fi

echo "📊 Service status:"
docker compose -f docker-compose.monitoring.yml ps

echo "🎉 Startup test completed!"
