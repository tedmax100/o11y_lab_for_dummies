#!/bin/bash

# OpenTelemetry Observability Lab startup script

set -e

echo "========================================="
echo "  OpenTelemetry Observability Lab"
echo "========================================="
echo ""

# Check Docker and Docker Compose
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not installed, please install Docker first"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose not installed, please install Docker Compose first"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check for running containers
if [ "$(docker ps -q -f name=o11y)" ]; then
    echo "⚠️  Detected running containers, stopping..."
    docker-compose down
    echo ""
fi

# Build and start services
echo "🏗️  Building service images..."
docker-compose build

echo ""
echo "🚀 Starting all services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "========================================="
echo "  Startup Complete!"
echo "========================================="
echo ""
echo "📍 Access URLs:"
echo "  - API Gateway:  http://localhost:8080"
echo "  - Grafana:      http://localhost:3000 (admin/admin)"
echo "  - Prometheus:   http://localhost:9090"
echo "  - Tempo:        http://localhost:3200"
echo "  - Loki:         http://localhost:3100"
echo ""
echo "🧪 Test Request:"
echo "  curl http://localhost:8080/api/process"
echo ""
echo "📝 View Logs:"
echo "  docker-compose logs -f"
echo ""
echo "🛑 Stop Services:"
echo "  docker-compose down"
echo ""
echo "========================================="
