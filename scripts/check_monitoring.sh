#!/bin/bash
# Quick verification script to check monitoring stack health

echo "🔍 Checking Monitoring Stack Health"
echo "====================================="
echo ""

# Function to check service
check_service() {
    local name=$1
    local url=$2
    local port=$3
    
    if curl -s "$url" > /dev/null 2>&1; then
        echo "✅ $name is UP (port $port)"
        return 0
    else
        echo "❌ $name is DOWN (port $port)"
        return 1
    fi
}

# Check Triton HTTP
check_service "Triton HTTP API" "http://localhost:8000/v2/health/ready" "8000"

# Check Triton Metrics
check_service "Triton Metrics" "http://localhost:8002/metrics" "8002"

# Check Prometheus
check_service "Prometheus" "http://localhost:9090/-/ready" "9090"

# Check Grafana
check_service "Grafana" "http://localhost:3000/api/health" "3000"

echo ""
echo "====================================="

# Check Prometheus targets
echo ""
echo "📊 Checking Prometheus Targets..."
targets=$(curl -s http://localhost:9090/api/v1/targets 2>/dev/null | grep -o '"health":"[^"]*"' | head -1)

if [[ $targets == *"up"* ]]; then
    echo "✅ Prometheus can reach Triton (target is UP)"
else
    echo "⚠️  Prometheus cannot reach Triton (check docker network)"
fi

# Check if metrics are being collected
echo ""
echo "📈 Checking Metrics Collection..."
metric_count=$(curl -s http://localhost:8002/metrics 2>/dev/null | grep -c "^nv_")

if [ "$metric_count" -gt 0 ]; then
    echo "✅ Triton is exposing $metric_count metrics"
else
    echo "⚠️  No metrics found from Triton"
fi

# Check Grafana datasource
echo ""
echo "🔌 Checking Grafana Datasource..."
datasource=$(curl -s http://localhost:3000/api/datasources/1 2>/dev/null)

if [[ $datasource == *"Prometheus"* ]]; then
    echo "✅ Grafana Prometheus datasource configured"
else
    echo "⚠️  Grafana datasource not configured (may be starting up)"
fi

echo ""
echo "====================================="
echo ""
echo "🌐 Quick Links:"
echo "  Triton API:    http://localhost:8000/v2"
echo "  Metrics:       http://localhost:8002/metrics"
echo "  Prometheus:    http://localhost:9090"
echo "  Grafana:       http://localhost:3000"
echo "  Dashboard:     http://localhost:3000/d/triton-metrics"
echo ""
echo "💡 Credentials:"
echo "  Grafana - admin / admin"
echo ""
