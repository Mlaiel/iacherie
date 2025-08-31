#!/bin/bash
# Monitoring Services Startup Script
set -e

echo "🚀 Starting Ainflue Monitoring Stack..."

# Clean up any existing containers
docker compose -f docker-compose.monitoring.yml down --remove-orphans || true

# Pull latest images
echo "📥 Pulling monitoring images..."
docker compose -f docker-compose.monitoring.yml pull --ignore-pull-failures

# Start monitoring services
echo "🔧 Starting monitoring services..."
docker compose -f docker-compose.monitoring.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 60

# Check Prometheus
echo "🩺 Checking Prometheus..."
if curl -f -s http://localhost:9090/-/healthy > /dev/null; then
    echo "✅ Prometheus is healthy"
else
    echo "❌ Prometheus is not responding"
fi

# Check Grafana
echo "🩺 Checking Grafana..."
if curl -f -s http://localhost:3000/api/health > /dev/null; then
    echo "✅ Grafana is healthy"
else
    echo "❌ Grafana is not responding"
fi

echo "📊 Monitoring services status:"
docker compose -f docker-compose.monitoring.yml ps

echo "🎉 Monitoring stack startup completed!"
echo "📊 Access URLs:"
echo "   Prometheus: http://localhost:9090"
echo "   Grafana: http://localhost:3000 (admin/admin123)"
echo "   AlertManager: http://localhost:9093"
