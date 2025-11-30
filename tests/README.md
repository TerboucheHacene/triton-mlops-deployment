# Tests

This directory contains test files for the Triton Inference Server deployment.

## 📁 Contents

### `locustfile.py` - Load Testing

Performance and load testing using Locust framework.

**Test Classes:**

1. **`TritonUser`** (Default) - Balanced load test
   - Mixed workload (light and heavy models)
   - Wait time: 1-3 seconds
   - Best for: General performance testing

2. **`HeavyLoadUser`** - Stress test
   - Large batch sizes (16-32)
   - Fast request rate
   - Best for: Stress testing and capacity planning

3. **`RealisticScenario`** - Production simulation
   - Session-based behavior
   - Mixed single/batch requests
   - Best for: Production readiness validation

## 🚀 Quick Start

### Install Locust

```bash
pip install locust
```

### Run Load Test

**Web UI (Recommended):**
```bash
locust -f tests/locustfile.py --host=http://localhost:8000

# Open browser to http://localhost:8089
```

**Headless Mode:**
```bash
locust -f tests/locustfile.py \
  --host=http://localhost:8000 \
  --users 50 \
  --spawn-rate 5 \
  --run-time 60s \
  --headless \
  --html report.html
```

**Quick Test Script:**
```bash
./scripts/run_load_test.sh
```

## 📊 Test Scenarios

### Example 1: Quick Test (10 users, 30s)

```bash
locust -f tests/locustfile.py \
  --host=http://localhost:8000 \
  --users 10 \
  --spawn-rate 2 \
  --run-time 30s \
  --headless
```

### Example 2: Stress Test (100 users)

```bash
locust -f tests/locustfile.py \
  --host=http://localhost:8000 \
  HeavyLoadUser \
  --users 100 \
  --spawn-rate 10 \
  --run-time 300s \
  --headless
```

## 📈 Interpreting Results

**Key Metrics:**
- **RPS**: Requests per second (target: > 100 for simple models)
- **p50**: Median response time (target: < 200ms)
- **p95**: 95th percentile latency (target: < 500ms)
- **Failures**: Should be < 1%

**Example Output:**
```
Type    Name                  # reqs  # fails  Avg    p50    p95    Max
POST    Linear Regression     10000      0    45ms   40ms   80ms   250ms
POST    Sentiment Analysis     6000      2   120ms  110ms  250ms   800ms
POST    ResNet Ensemble        4000      5   450ms  420ms  900ms  2000ms
```

## 🔧 Prerequisites

Before running tests:

1. **Start Triton Server:**
   ```bash
   cd configs && docker-compose up -d
   sleep 30  # Wait for models to load
   ```

2. **Verify Server Ready:**
   ```bash
   curl http://localhost:8000/v2/health/ready
   ```

3. **Check Models Loaded:**
   ```bash
   curl -X POST http://localhost:8000/v2/repository/index
   ```

## 📚 Documentation

For complete guide, see: **[docs/LOAD_TESTING.md](../docs/LOAD_TESTING.md)**

Topics covered:
- Installation and setup
- Running different test scenarios
- Interpreting results
- Performance tuning
- Troubleshooting
- CI/CD integration

## 🎯 Performance Targets

| Model | Target RPS | Target p50 | Target p95 |
|-------|-----------|-----------|-----------|
| Linear Regression | > 500 | < 50ms | < 100ms |
| Sentiment Analysis | > 50 | < 150ms | < 300ms |
| ResNet50 | > 100 | < 150ms | < 300ms |
| ResNet Ensemble | > 50 | < 500ms | < 1000ms |

## 🐛 Troubleshooting

**High failure rate?**
- Increase shared memory: `shm_size: '4gb'` in docker-compose.yaml
- Check Triton logs: `docker logs triton-server`

**Slow response times?**
- Enable GPU in model config
- Increase model instances
- Optimize dynamic batching

**Connection errors?**
- Verify Triton is running: `docker ps | grep triton`
- Check port mapping: `docker port triton-server`

## 🧪 Future Tests

Planned additions:
- [ ] Unit tests for model inference
- [ ] Integration tests for ensemble pipelines
- [ ] Model accuracy tests
- [ ] API contract tests

## 📝 Contributing

When adding new tests:
1. Follow existing patterns in `locustfile.py`
2. Add documentation to this README
3. Update performance targets
4. Test thoroughly before committing

---

**For detailed information, see: [docs/LOAD_TESTING.md](../docs/LOAD_TESTING.md)**
