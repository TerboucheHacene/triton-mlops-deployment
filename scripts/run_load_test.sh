#!/bin/bash

# ============================================
# Quick Load Test Runner
# ============================================
# This script runs a quick load test on your Triton server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "Triton Load Test Runner"
echo "=========================================="
echo ""

# Check if Triton is running
echo "Checking if Triton server is running..."
if ! curl -s http://localhost:8000/v2/health/ready > /dev/null; then
    echo "❌ Error: Triton server is not running!"
    echo ""
    echo "Please start Triton first:"
    echo "  cd configs && docker-compose up -d"
    echo ""
    exit 1
fi
echo "✓ Triton server is ready"
echo ""

# Check if locust is installed
echo "Checking if Locust is installed..."
if ! command -v locust &> /dev/null; then
    echo "❌ Error: Locust is not installed!"
    echo ""
    echo "Install with: pip install locust"
    echo ""
    exit 1
fi
echo "✓ Locust is installed"
echo ""

# Run options
echo "=========================================="
echo "Select Load Test Type:"
echo "=========================================="
echo "1. Quick Test (10 users, 30 seconds)"
echo "2. Standard Test (50 users, 2 minutes)"
echo "3. Stress Test (100 users, 5 minutes)"
echo "4. Custom (Web UI)"
echo ""

read -p "Select option (1-4): " choice

case $choice in
    1)
        echo ""
        echo "Running Quick Test..."
        cd "$REPO_ROOT"
        locust -f tests/locustfile.py \
            --host=http://localhost:8000 \
            --users 10 \
            --spawn-rate 2 \
            --run-time 30s \
            --headless \
            --html load-test-quick.html
        
        echo ""
        echo "✓ Test complete! Report saved to: load-test-quick.html"
        ;;
    
    2)
        echo ""
        echo "Running Standard Test..."
        cd "$REPO_ROOT"
        locust -f tests/locustfile.py \
            --host=http://localhost:8000 \
            --users 50 \
            --spawn-rate 5 \
            --run-time 120s \
            --headless \
            --html load-test-standard.html
        
        echo ""
        echo "✓ Test complete! Report saved to: load-test-standard.html"
        ;;
    
    3)
        echo ""
        echo "Running Stress Test..."
        cd "$REPO_ROOT"
        locust -f tests/locustfile.py \
            --host=http://localhost:8000 \
            HeavyLoadUser \
            --users 100 \
            --spawn-rate 10 \
            --run-time 300s \
            --headless \
            --html load-test-stress.html
        
        echo ""
        echo "✓ Test complete! Report saved to: load-test-stress.html"
        ;;
    
    4)
        echo ""
        echo "Starting Locust Web UI..."
        echo ""
        echo "Open your browser to: http://localhost:8089"
        echo "Press Ctrl+C to stop"
        echo ""
        cd "$REPO_ROOT"
        locust -f tests/locustfile.py --host=http://localhost:8000
        ;;
    
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "Load Test Summary"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Open the HTML report in your browser"
echo "2. Check for high failure rates (should be < 5%)"
echo "3. Monitor response times (p95 should be < 1000ms)"
echo "4. Review Docker stats: docker stats triton-server"
echo ""
echo "For more details, see: docs/LOAD_TESTING.md"
