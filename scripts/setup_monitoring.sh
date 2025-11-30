#!/bin/bash
# Setup and start Triton with Prometheus + Grafana monitoring

set -e

echo "🚀 Setting up Triton Inference Server with Monitoring"
echo "======================================================"
echo ""

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose not found"
    echo "   Please install docker-compose first"
    exit 1
fi

# Navigate to configs directory
cd "$(dirname "$0")/../configs" || exit 1

echo "📦 Stopping existing services (if any)..."
# Stop docker-compose services
docker-compose down 2>/dev/null || true

# Also stop standalone triton_server if it exists
if docker ps -a --format '{{.Names}}' | grep -q '^triton_server$'; then
    echo "  Stopping standalone triton_server container..."
    docker stop triton_server 2>/dev/null || true
    docker rm triton_server 2>/dev/null || true
fi

echo ""
echo "🏗️  Starting services..."
echo "  - Triton Server (inference)"
echo "  - Prometheus (metrics collection)"
echo "  - Grafana (visualization)"
echo ""

docker-compose up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Check Triton health
echo ""
echo "🔍 Checking Triton Server..."
if curl -s http://localhost:8000/v2/health/ready > /dev/null 2>&1; then
    echo "  ✅ Triton Server is ready (port 8000)"
else
    echo "  ⚠️  Triton Server is starting... (may take 30-60 seconds for models to load)"
fi

# Check Prometheus
echo ""
echo "🔍 Checking Prometheus..."
if curl -s http://localhost:9090/-/ready > /dev/null 2>&1; then
    echo "  ✅ Prometheus is ready (port 9090)"
else
    echo "  ⚠️  Prometheus is starting..."
fi

# Check Grafana
echo ""
echo "🔍 Checking Grafana..."
if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "  ✅ Grafana is ready (port 3000)"
else
    echo "  ⚠️  Grafana is starting..."
fi

echo ""
echo "======================================================"
echo "✅ Setup complete!"
echo ""
echo "📊 Access your services:"
echo "  - Triton HTTP API:     http://localhost:8000"
echo "  - Triton Metrics:      http://localhost:8002/metrics"
echo "  - Prometheus UI:       http://localhost:9090"
echo "  - Grafana Dashboard:   http://localhost:3000"
echo ""
echo "🔑 Grafana credentials:"
echo "  Username: admin"
echo "  Password: admin"
echo ""
echo "📈 Dashboard will be available at:"
echo "   http://localhost:3000/d/triton-metrics"
echo ""
echo "💡 Useful commands:"
echo "  - View logs:        docker-compose logs -f [triton|prometheus|grafana]"
echo "  - Stop services:    docker-compose down"
echo "  - Restart services: docker-compose restart"
echo ""
echo "🧪 Generate load to see metrics:"
echo "  python3 -m locust -f tests/locustfile_resnet.py --host=http://localhost:8000"
echo ""
echo "======================================================"
