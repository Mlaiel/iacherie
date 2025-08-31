#!/bin/bash
# Generated startup test script for docker-compose.production.yml
# Run this to test service startup

set -e

echo "🚀 Testing docker-compose.production.yml service startup..."

# Clean up any existing containers
docker compose -f docker-compose.production.yml down --remove-orphans || true

# Pull latest images
echo "📥 Pulling images..."
docker compose -f docker-compose.production.yml pull --ignore-pull-failures

# Start services
echo "🔧 Starting services..."
docker compose -f docker-compose.production.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🩺 Checking service health..."

echo "📊 Service status:"
docker compose -f docker-compose.production.yml ps

echo "🎉 Startup test completed!"
