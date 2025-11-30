# Load Testing & Dynamic Batching Guide

Complete guide for load testing your Triton Inference Server and verifying dynamic batching performance.

---

## 📋 Table of Contents

### Part 1: Load Testing
- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Running Tests](#running-tests)
- [Interpreting Results](#interpreting-results)

### Part 2: Dynamic Batching
- [What is Dynamic Batching?](#what-is-dynamic-batching)
- [Verifying Batching Works](#verifying-batching-works)
- [Batching Configuration](#batching-configuration)
- [Tuning for Performance](#tuning-for-performance)

### Part 3: Advanced Topics
- [Performance Benchmarking](#performance-benchmarking)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [CI/CD Integration](#cicd-integration)

---

# Part 1: Load Testing

## Overview

**Load testing** helps you measure and validate your inference server's performance before production deployment.

### Why Load Test?

- ✅ Measure throughput (requests/second)
- ✅ Identify bottlenecks
- ✅ Test scalability with concurrent users
- ✅ Measure latency under load
- ✅ Validate dynamic batching effectiveness
- ✅ Stress test system limits

### Tools We Use

- **Locust** - Python-based load testing with realistic user simulation
- **Triton Metrics** - Built-in Prometheus metrics for monitoring
- **Custom Scripts** - Specialized batching verification tools

---

## Installation

### Install Required Packages

```bash
# Install Locust and dependencies
pip install locust tritonclient[http]

# Or use requirements.txt
pip install -r requirements.txt
```

### Verify Installation

```bash
# Check Locust version
python3 -m locust --version
# Expected: locust 2.42.6 or higher

# Verify Triton is running
curl http://localhost:8000/v2/health/ready
# Expected: {}
```

---

## Quick Start

### 1. Start Triton Server

```bash
# Ensure Triton is running
docker ps | grep triton_server

# If not running, start it
docker-compose up -d triton_server

# Wait for models to load (~30 seconds)
sleep 30
```

### 2. Run Load Test

```bash
# Web UI mode (recommended for interactive testing)
python3 -m locust -f tests/locustfile_resnet.py --host=http://localhost:8000

# Open browser to: http://localhost:8089
# Configure: Users=10, Spawn rate=2
# Click "Start swarming"
```

### 3. Check Results

While test is running, you'll see:
- 📊 Real-time request statistics
- 📈 Response time charts
- 📉 Requests/second graphs
- ✅ Success/failure rates

---

## Running Tests

### Web UI Mode (Interactive)

**Best for**: Development, exploration, real-time monitoring

```bash
python3 -m locust -f tests/locustfile_resnet.py --host=http://localhost:8000
```

**Features:**
- Real-time statistics dashboard
- Interactive controls (start/stop/adjust users)
- Response time charts and graphs
- Detailed failure logs with tracebacks

**Access**: http://localhost:8089

---

### Headless Mode (Automated)

**Best for**: CI/CD, benchmarking, automated testing

```bash
# Run 30-second test with 20 concurrent users
python3 -m locust -f tests/locustfile_resnet.py \
  --host=http://localhost:8000 \
  --users 20 \
  --spawn-rate 5 \
  --run-time 30s \
  --headless \
  --html load-test-report.html
```

**Parameters:**
- `--users`: Total concurrent users simulating requests
- `--spawn-rate`: How many users spawn per second
- `--run-time`: Test duration (e.g., `30s`, `5m`, `1h`)
- `--headless`: Run without web UI
- `--html`: Save results to HTML report

**Example output:**
```
Type     Name                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|------------------------------|-----------|---------|-------|-------|-------|-------|--------|-----------
POST     ResNet Standard 224x224       231           0     |    282      15    9543     20 |   7.70    0.00
POST     ResNet Small (128-192)        131           0     |    283      14    9987     21 |   4.37    0.00
POST     ResNet Large (256-384)        103           0     |    281      14   10002     21 |   3.43    0.00
POST     ResNet Variable Sizes          50           0     |    287      15    9996     21 |   1.67    0.00
--------|------------------------------|-----------|---------|-------|-------|-------|-------|--------|-----------
         Aggregated                     515           0     |    282       5   10002     20 |  17.17    0.00
```

---

### Test Scenarios in locustfile_resnet.py

The ResNet load test includes **4 weighted scenarios**:

#### 1. **Standard 224x224 Images** (Weight: 5 - Most Frequent)
- Tests with standard ImageNet size (224x224)
- Represents typical production workload
- Fastest preprocessing (no resize needed)

#### 2. **Small Images** (Weight: 3)
- Tests: 128x128, 160x160, 192x192
- Validates preprocessing handles various input sizes
- Tests upscaling performance

#### 3. **Large Images** (Weight: 2)
- Tests: 256x256, 320x320, 384x384
- Validates downscaling performance
- Tests memory handling for large inputs

#### 4. **Variable Rectangular Sizes** (Weight: 1)
- Tests: 200x300, 300x200, 256x192, 512x256, etc.
- Validates aspect ratio handling
- Tests edge cases

**Why these scenarios?**
- Realistic production workloads have varied image sizes
- Tests preprocessing flexibility (our config accepts any size)
- Validates dynamic batching works regardless of input size

---

## Interpreting Results

### Key Metrics to Watch

#### 1. **Requests Per Second (RPS / Throughput)**

Measures how many inference requests the server handles per second.

**Targets for ResNet Ensemble:**
- ✅ **Good**: > 15 RPS (with 10-20 users)
- ⚠️ **Average**: 10-15 RPS
- ❌ **Poor**: < 10 RPS

**What affects RPS:**
- Dynamic batching configuration (higher batch = higher RPS)
- Number of model instances
- GPU vs CPU
- Preprocessing complexity

---

#### 2. **Response Time (Latency)**

Time from request sent to response received.

**Key Percentiles:**
- **P50 (Median)**: 50% of requests faster than this
- **P95**: 95% of requests faster than this (service quality indicator)
- **P99**: 99% of requests faster than this (tail latency)

**Targets:**
- ✅ **Excellent**: P50 < 50ms, P95 < 200ms
- ⚠️ **Good**: P50 < 200ms, P95 < 500ms
- ❌ **Poor**: P50 > 500ms, P95 > 2000ms

**Important**: With dynamic batching, expect higher variance:
- Some requests are fast (batched immediately)
- Some requests wait (queued for batch formation)
- This is **normal and expected** with batching!

---

#### 3. **Failure Rate**

Percentage of requests that failed.

**Targets:**
- ✅ **Excellent**: 0%
- ⚠️ **Acceptable**: < 1%
- ❌ **Problematic**: > 5%

**Common failure causes:**
- Server overload (reduce users or increase capacity)
- Memory exhaustion (increase Docker shm_size)
- Model errors (check Triton logs)

---

#### 4. **Response Time Distribution**

The spread between min, median, and max response times.

**Healthy pattern:**
- Min: Very fast (5-20ms) - requests that batched quickly
- Median: Moderate (20-100ms) - typical batched requests
- Max: Higher (100-500ms) - requests that waited for batch formation

**Unhealthy pattern:**
- All responses similar time → No batching happening!
- Max >> 10x median → Configuration issue or overload

---

### Sample Results Analysis

```
Type     Name                          # reqs  # fails |   Avg   Min   Max   Med |  req/s
---------|------------------------------|--------|--------|------|-----|-------|-----|-------
POST     ResNet Ensemble                515       0    |  282ms  5ms  10000ms  20ms| 17.26
```

**Analysis:**
- ✅ **Zero failures**: Server handling load well
- ✅ **17.26 req/s**: Good throughput for ResNet ensemble
- ⚠️ **Wide latency range** (5ms - 10s): 
  - Good sign: Shows batching is working (some fast, some queued)
  - Max 10s is high (likely cold start or first requests)
- ✅ **P50 of 20ms**: Most requests are fast

**Action**: Check batching metrics to confirm effectiveness!

---

# Part 2: Dynamic Batching

## What is Dynamic Batching?

**Dynamic batching** is Triton's ability to automatically combine multiple individual inference requests into a single batch before sending to the GPU.

### Without Dynamic Batching ❌

```
Client 1 → [Image] → GPU inference → Result 1
Client 2 → [Image] → GPU inference → Result 2
Client 3 → [Image] → GPU inference → Result 3
...
100 requests = 100 GPU calls = Inefficient!
```

### With Dynamic Batching ✅

```
Client 1 → [Image] ↘
Client 2 → [Image] → Triton queues → [Batch of 8] → GPU inference → Split results
Client 3 → [Image] ↗
...
100 requests ≈ 12-25 GPU calls = Much more efficient!
```

### Benefits

- **🚀 Higher Throughput**: Process more requests per second
- **💰 Better GPU Utilization**: GPUs are optimized for batch operations
- **⚡ Lower Cost per Request**: Amortize inference cost across multiple requests
- **📊 Scalability**: Handle more concurrent users without adding hardware

### Trade-offs

- **⏱️ Slightly Higher Latency**: Requests wait briefly to form batches
- **🎯 Configuration Required**: Need to tune batch sizes and queue delays
- **🔄 Works Best with Load**: Low traffic = minimal batching

---

## Verifying Batching Works

After running load tests, you need to verify that dynamic batching is actually happening.

### Method 1: Use check_batching.py ⭐ (RECOMMENDED)

This is the **primary tool** for batching verification.

```bash
# Check current batching status
python3 tests/check_batching.py
```

**Example output (Good batching):**

```
🔍 Checking Triton Dynamic Batching Status...

📊 Metrics for 'resnet_model':
============================================================
✓ Total Requests:        840
✓ Inference Executions:  211
✓ Queue Time (total):    149.83s
✓ Compute Time (total):  185.41s
============================================================

🎯 Batching Analysis:
============================================================
Average Batch Size:      3.98 requests/batch
Batching Efficiency:     74.9% GPU call reduction
Avg Queue Time/Request:  178.37ms
Avg Compute/Execution:   878.73ms
============================================================

💡 Interpretation:
✅ BATCHING IS WORKING! Average 4.0 requests combined per GPU call.
   840 requests executed in only 211 GPU calls.
   GPU utilization improved by 74.9%!
```

**What to look for:**
- ✅ **Average Batch Size > 2.0**: Good batching
- ✅ **Batching Efficiency > 50%**: Significant GPU call reduction
- ✅ **Queue Time > 0**: Requests are waiting to batch (expected)
- ❌ **Average Batch Size ≈ 1.0**: No batching (increase load or queue delay)

---

### Method 2: Real-Time Monitoring

Monitor batching as requests come in.

```bash
# Monitor for 60 seconds, update every 5 seconds
python3 tests/check_batching.py --monitor --duration 60 --interval 5
```

**In another terminal, generate load:**

```bash
python3 -m locust -f tests/locustfile_resnet.py \
  --host=http://localhost:8000 \
  --users 20 \
  --headless
```

**Example monitoring output:**

```
📡 Monitoring batching for 60 seconds (refresh every 5s)...

⏱️  [14:23:10] +50 requests in +6 executions → avg batch: 8.3
⏱️  [14:23:15] +40 requests in +5 executions → avg batch: 8.0
⏱️  [14:23:20] +35 requests in +3 executions → avg batch: 11.7
```

This shows batching happening in **real-time**!

---

### Method 3: Raw Triton Metrics (Manual)

Query Triton's Prometheus metrics directly.

```bash
# Get all metrics for resnet_model
curl -s http://localhost:8002/metrics | grep "resnet_model"

# Calculate batch ratio manually
curl -s http://localhost:8002/metrics | \
  grep -E "nv_inference_(request_success|exec_count).*resnet_model"
```

**Key metrics:**
- `nv_inference_request_success`: Total requests received
- `nv_inference_exec_count`: Total GPU executions (batch calls)
- **Batch ratio** = requests / executions

If `840 requests / 211 executions = 3.98 avg batch size` → ✅ Batching works!

---

### Method 4: Load Test Performance Patterns

Good batching shows specific performance characteristics:

**Indicators batching is working:**
- ✅ Concurrent requests are **faster** than sequential
- ✅ Wide latency distribution (some fast, some queued)
- ✅ Throughput increases with more concurrent users
- ✅ P50 latency is much lower than P95 (queue variation)

**Indicators batching is NOT working:**
- ❌ All requests take similar time (no variance)
- ❌ Concurrent not faster than sequential
- ❌ Throughput doesn't improve with more users
- ❌ Average batch size ≈ 1.0 in metrics

---

## Batching Configuration

Configuration lives in `model_repository/resnet_model/config.pbtxt`

### Current Configuration

```protobuf
name: "resnet_model"
backend: "pytorch"
max_batch_size: 32

dynamic_batching {
  preferred_batch_size: [ 4, 8, 16 ]
  max_queue_delay_microseconds: 100000  # 100ms
}

instance_group [{ kind: KIND_GPU }]
```

### Key Parameters Explained

#### 1. `max_batch_size: 32`

**What it does**: Maximum number of requests that can be batched together.

**Considerations:**
- Higher = Better GPU utilization but more memory
- Must fit in GPU memory: `batch_size × model_input_size × 4 bytes`
- For ResNet50: `32 × 3 × 224 × 224 × 4 bytes ≈ 192 MB` (plus model weights)

**Recommendations:**
- Small models: 64-128
- Medium models (ResNet50): 16-32
- Large models (BERT, GPT): 4-16

---

#### 2. `preferred_batch_size: [ 4, 8, 16 ]`

**What it does**: Target batch sizes Triton tries to hit. Triton will prefer forming these batch sizes when possible.

**How it works:**
- If 4+ requests queued → Send batch of 4
- If 8+ requests queued → Send batch of 8
- If 16+ requests queued → Send batch of 16
- If timeout reached → Send whatever is queued

**Best practices:**
- Use powers of 2: `[4, 8, 16, 32]` (GPU optimization)
- Start small, increase based on load patterns
- Match your typical concurrent load

**Example:**
- Light load (5 users): `preferred_batch_size: [2, 4]`
- Medium load (20 users): `preferred_batch_size: [4, 8, 16]` ← Current
- Heavy load (100+ users): `preferred_batch_size: [16, 32, 64]`

---

#### 3. `max_queue_delay_microseconds: 100000`

**What it does**: Maximum time (in microseconds) Triton waits to accumulate requests before forming a batch.

**Current setting**: 100,000 microseconds = **100 milliseconds**

**How it works:**
```
Request arrives → Start timer (100ms) → Keep queuing incoming requests
↓
Timer expires OR preferred_batch_size reached
↓
Send batch to GPU
```

**Trade-off:**
- **Higher delay** = More batching (better throughput) but higher latency
- **Lower delay** = Lower latency but less batching (lower throughput)

**Typical values:**
- **Real-time systems**: 1,000-5,000 µs (1-5ms) - Prioritize latency
- **Balanced** (current): 100,000 µs (100ms) - Good batching with acceptable latency
- **Batch processing**: 500,000-1,000,000 µs (500ms-1s) - Maximum throughput

---

## Tuning for Performance

### Performance Goal: Maximize Throughput

**Use case**: Batch processing, high-volume inference, cost optimization

```protobuf
max_batch_size: 64
preferred_batch_size: [ 16, 32, 64 ]
max_queue_delay_microseconds: 500000  # 500ms - wait longer for bigger batches
```

**Expected results:**
- ✅ Higher RPS (requests per second)
- ✅ Better GPU utilization (larger batches)
- ✅ Lower cost per request
- ⚠️ Higher latency (P95 may be 500-1000ms)

---

### Performance Goal: Minimize Latency

**Use case**: Real-time applications, user-facing APIs, strict SLAs

```protobuf
max_batch_size: 16
preferred_batch_size: [ 4, 8 ]
max_queue_delay_microseconds: 5000  # 5ms - quick batching only
```

**Expected results:**
- ✅ Lower latency (P50 < 100ms, P95 < 200ms)
- ✅ More predictable response times
- ⚠️ Lower throughput (smaller batches)
- ⚠️ Lower GPU utilization

---

### Performance Goal: Balanced (Current Setup)

**Use case**: General purpose, mixed workload, development/testing

```protobuf
max_batch_size: 32
preferred_batch_size: [ 4, 8, 16 ]
max_queue_delay_microseconds: 100000  # 100ms
```

**Expected results:**
- ✅ Good batching (avg 4-8 requests/batch)
- ✅ Reasonable latency (P50 ~50ms, P95 ~500ms)
- ✅ Decent throughput (15-30 RPS for ResNet)
- ✅ Balanced cost/performance

**This is our current configuration** - proven to achieve:
- Average batch size: ~4.0
- Batching efficiency: ~75% GPU call reduction
- Throughput: 17+ RPS

---

### Tuning Workflow

```bash
# 1. Start with current config
python3 -m locust -f tests/locustfile_resnet.py --host=http://localhost:8000 \
  --users 20 --run-time 60s --headless

# 2. Check batching effectiveness
python3 tests/check_batching.py

# 3. If average batch size < 2, increase queue delay
# Edit model_repository/resnet_model/config.pbtxt
# Change: max_queue_delay_microseconds: 100000 → 200000

# 4. Restart Triton
docker restart triton_server && sleep 10

# 5. Retest
python3 -m locust -f tests/locustfile_resnet.py --host=http://localhost:8000 \
  --users 20 --run-time 60s --headless

# 6. Check metrics again
python3 tests/check_batching.py

# 7. Repeat until satisfied
```

---

### When Batching Might NOT Help

Dynamic batching is great, but not always:

❌ **Very low traffic** (< 5 req/min)
- Not enough concurrent requests to batch
- Solution: Accept lower throughput or batch at client side

❌ **Extremely latency-sensitive** (< 10ms SLA)
- Queue delay adds latency
- Solution: Disable batching, use multiple model instances instead

❌ **Variable input sizes with explicit batching**
- Our ResNet setup handles this (preprocessor normalizes to 224x224)
- But some models can't batch different input shapes

❌ **Model doesn't support batching**
- Some custom models aren't batch-aware
- Check model can handle `[batch_size, ...input_shape...]`

---

# Part 3: Advanced Topics

## Performance Benchmarking

### Baseline vs Load Testing

Compare performance under different load conditions.

```bash
# Baseline (no load - single user)
python3 -m locust -f tests/locustfile_resnet.py \
  --host=http://localhost:8000 \
  --users 1 \
  --spawn-rate 1 \
  --run-time 30s \
  --headless \
  --html baseline.html

# Low load (10 users)
python3 -m locust -f tests/locustfile_resnet.py \
  --host=http://localhost:8000 \
  --users 10 \
  --spawn-rate 2 \
  --run-time 60s \
  --headless \
  --html low_load.html

# Medium load (50 users)
python3 -m locust -f tests/locustfile_resnet.py \
  --host=http://localhost:8000 \
  --users 50 \
  --spawn-rate 5 \
  --run-time 120s \
  --headless \
  --html medium_load.html

# High load (100 users - stress test)
python3 -m locust -f tests/locustfile_resnet.py \
  --host=http://localhost:8000 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 180s \
  --headless \
  --html high_load.html
```

**Compare results:**
- Baseline: Best possible latency (no batching needed)
- Low: Should show some batching, good latency
- Medium: Best batching efficiency, higher throughput
- High: Test limits, may show failures or slowdown

---

### Performance Targets

Expected performance for ResNet Ensemble (single GPU):

| Load | Users | RPS | P50 Latency | P95 Latency | Batch Size |
|------|-------|-----|-------------|-------------|------------|
| Baseline | 1 | ~8 | 115ms | 120ms | 1.0 (no batching) |
| Low | 10 | ~15 | 50ms | 200ms | 2-3 |
| Medium | 50 | ~25 | 80ms | 500ms | 4-8 |
| High | 100 | ~30 | 150ms | 2000ms | 8-16 |

*Note: Performance varies by hardware (GPU model, CPU, RAM)*

---

## Best Practices

### 1. Always Warm Up Models

```bash
# Before load testing, send a few requests to warm up
for i in {1..5}; do
  curl -X POST http://localhost:8000/v2/models/resnet_model/infer \
    -H "Content-Type: application/json" \
    -d @sample_request.json
done
```

**Why?** First requests are always slower:
- Model loading
- CUDA initialization
- Memory allocation

---

### 2. Monitor System Resources

```bash
# In separate terminal during load test
docker stats triton_server

# Watch for:
# - CPU: Should be < 90% (if higher, need more CPU)
# - Memory: Should have headroom (if near limit, increase Docker memory)
# - GPU: Check utilization (higher batch = higher GPU%)
```

---

### 3. Test Realistic Scenarios

✅ **Do:**
- Mix different image sizes (like locustfile_resnet.py does)
- Simulate real user wait times
- Test peak hours load
- Include error scenarios

❌ **Don't:**
- Only test with perfect inputs
- Use unrealistic burst patterns
- Skip warm-up phase
- Ignore failures

---

### 4. Iterate on Configuration

```bash
# Test → Measure → Tune → Repeat
while [[ $batch_efficiency -lt 70 ]]; do
  # Run load test
  locust ...
  
  # Check metrics
  batch_efficiency=$(python3 tests/check_batching.py | grep "Efficiency" | awk '{print $3}')
  
  # Adjust config
  # Increase max_queue_delay or preferred_batch_size
  
  # Restart and retest
  docker restart triton_server
done
```

---

### 5. Document Your Findings

Keep a performance log:

```
Date: 2025-11-30
Config: max_batch_size=32, queue_delay=100ms, preferred=[4,8,16]
Load: 20 users, 60s
Results:
  - RPS: 17.26
  - P50: 20ms, P95: 150ms
  - Batch size: 3.98 avg
  - Efficiency: 74.9%
Status: ✅ Production ready
```

---

## Troubleshooting

### Issue: "Average batch size is 1.0" (No Batching)

**Symptoms:**
```
Average Batch Size:      1.02 requests/batch
Batching Efficiency:     2.0% GPU call reduction
```

**Causes & Solutions:**

1. **Not enough concurrent load**
   ```bash
   # Increase users in load test
   --users 50  # instead of 10
   ```

2. **Queue delay too short**
   ```protobuf
   # In config.pbtxt
   max_queue_delay_microseconds: 100000  # Increase from 1000
   ```

3. **Requests too spread out**
   ```python
   # In locustfile, reduce wait time
   wait_time = between(0.1, 0.5)  # Instead of between(1, 3)
   ```

---

### Issue: "High latency (P95 > 2000ms)"

**Symptoms:**
```
P50: 50ms, P95: 3000ms  # Large gap!
```

**Causes & Solutions:**

1. **Queue delay too high**
   ```protobuf
   # Reduce queue delay for lower latency
   max_queue_delay_microseconds: 10000  # 10ms instead of 100ms
   ```

2. **Batch size too large**
   ```protobuf
   max_batch_size: 16  # Reduce from 32
   preferred_batch_size: [ 4, 8 ]
   ```

3. **GPU overloaded**
   ```protobuf
   # Add more model instances
   instance_group [{
     kind: KIND_GPU
     count: 2  # Run 2 instances in parallel
   }]
   ```

---

### Issue: "High failure rate (> 5%)"

**Symptoms:**
```
# reqs  # fails | Failure rate
1000      50    | 5%
```

**Causes & Solutions:**

1. **Shared memory exhausted** (Python backend)
   ```yaml
   # In docker-compose.yaml
   services:
     triton_server:
       shm_size: '4gb'  # Increase from 1gb
   ```

2. **Request queue full**
   ```protobuf
   # In config.pbtxt, reduce queue delay
   max_queue_delay_microseconds: 10000
   ```

3. **Model timeout**
   ```bash
   # Check Triton logs for errors
   docker logs triton_server 2>&1 | tail -100
   ```

---

### Issue: "Connection refused"

**Error:**
```
ConnectionError: HTTPConnectionPool(host='localhost', port=8000): 
Max retries exceeded
```

**Solutions:**

```bash
# 1. Check Triton is running
docker ps | grep triton_server

# 2. Check port mapping
docker port triton_server

# 3. Check server health
curl http://localhost:8000/v2/health/ready

# 4. Restart if needed
docker restart triton_server && sleep 10
```

---

### Issue: "Batch sizes too small despite configuration"

**Problem**: Average batch size is 1.5-2.0, but you configured preferred=[8,16]

**Explanation**: Preferred batch sizes are **targets**, not guarantees.

**Triton's batching logic:**
1. If `>= 8 requests` queued → Send batch of 8 ✓
2. If `< 8 requests` queued → Wait for `max_queue_delay`
3. If timer expires with only 3 requests → Send batch of 3 (not 8)

**Solutions:**
- Increase load (more concurrent users)
- Increase `max_queue_delay` (wait longer for requests)
- Lower `preferred_batch_size` to match actual load: `[2, 4]`

---

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/load-test.yml
name: Load Test

on:
  pull_request:
    branches: [ main ]

jobs:
  load-test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install locust tritonclient[http]
      
      - name: Start Triton Server
        run: |
          docker-compose up -d triton_server
          sleep 60  # Wait for models to load
      
      - name: Verify server health
        run: |
          curl --retry 10 --retry-delay 5 http://localhost:8000/v2/health/ready
      
      - name: Run load test
        run: |
          python3 -m locust -f tests/locustfile_resnet.py \
            --host=http://localhost:8000 \
            --users 10 \
            --spawn-rate 2 \
            --run-time 60s \
            --headless \
            --html load-test-report.html
      
      - name: Check batching efficiency
        run: |
          python3 tests/check_batching.py > batching-report.txt
          cat batching-report.txt
          
          # Fail if batching efficiency < 50%
          efficiency=$(grep "Batching Efficiency" batching-report.txt | awk '{print $3}' | sed 's/%//')
          if (( $(echo "$efficiency < 50" | bc -l) )); then
            echo "❌ Batching efficiency too low: $efficiency%"
            exit 1
          fi
      
      - name: Upload reports
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: load-test-reports
          path: |
            load-test-report.html
            batching-report.txt
      
      - name: Stop Triton
        if: always()
        run: docker-compose down
```

---

## Quick Reference

### Essential Commands

```bash
# ===== LOAD TESTING =====

# Interactive web UI
python3 -m locust -f tests/locustfile_resnet.py --host=http://localhost:8000

# Automated test (30 seconds, 20 users)
python3 -m locust -f tests/locustfile_resnet.py \
  --host=http://localhost:8000 \
  --users 20 --spawn-rate 5 --run-time 30s \
  --headless --html report.html

# ===== BATCHING VERIFICATION =====

# Check current batching status
python3 tests/check_batching.py

# Monitor batching in real-time
python3 tests/check_batching.py --monitor --duration 60 --interval 5

# Check raw Triton metrics
curl -s http://localhost:8002/metrics | grep resnet_model

# ===== CONFIGURATION =====

# Edit batching config
vim model_repository/resnet_model/config.pbtxt

# Restart Triton after config changes
docker restart triton_server && sleep 10

# ===== HEALTH CHECKS =====

# Check server is ready
curl http://localhost:8000/v2/health/ready

# Check model is ready
curl http://localhost:8000/v2/models/resnet_model/ready

# List all models
curl http://localhost:8000/v2/models
```

---

### "I want to..." Cookbook

**I want to test if my server can handle 50 concurrent users:**
```bash
python3 -m locust -f tests/locustfile_resnet.py --host=http://localhost:8000 \
  --users 50 --spawn-rate 5 --run-time 120s --headless --html report.html
```

**I want to verify dynamic batching is working:**
```bash
# Run load test first
python3 -m locust -f tests/locustfile_resnet.py --host=http://localhost:8000 \
  --users 20 --run-time 60s --headless

# Then check metrics
python3 tests/check_batching.py
```

**I want to maximize throughput (don't care about latency):**
```protobuf
# In model_repository/resnet_model/config.pbtxt
max_batch_size: 64
preferred_batch_size: [ 16, 32, 64 ]
max_queue_delay_microseconds: 500000
```

**I want to minimize latency (throughput is secondary):**
```protobuf
# In model_repository/resnet_model/config.pbtxt
max_batch_size: 16
preferred_batch_size: [ 4, 8 ]
max_queue_delay_microseconds: 5000
```

**I want to run tests in CI/CD pipeline:**
```bash
python3 -m locust -f tests/locustfile_resnet.py \
  --host=http://localhost:8000 \
  --users 10 --spawn-rate 2 --run-time 60s \
  --headless --html report.html
```

**I want to find the breaking point of my server:**
```bash
# Gradually increase load until failures occur
for users in 10 20 50 100 200; do
  python3 -m locust -f tests/locustfile_resnet.py \
    --host=http://localhost:8000 \
    --users $users --run-time 60s --headless \
    --html "stress-test-${users}users.html"
  sleep 30
done
```

---

## Summary

### Load Testing Workflow

```
1. Start Triton Server
   ↓
2. Run Load Test (locustfile_resnet.py)
   ↓
3. Check Batching Metrics (check_batching.py)
   ↓
4. Analyze Results (RPS, latency, batch efficiency)
   ↓
5. Tune Configuration (if needed)
   ↓
6. Restart & Retest
   ↓
7. Deploy to Production ✅
```

### Key Takeaways

✅ **Load testing** validates your system handles production load  
✅ **Dynamic batching** dramatically improves GPU efficiency (50-80% reduction in GPU calls)  
✅ **Configuration matters** - tune based on latency vs throughput goals  
✅ **Monitor continuously** - use check_batching.py to verify batching works  
✅ **Iterate** - test, measure, tune, repeat  

### Tools Reference

- **`tests/locustfile_resnet.py`** - Load testing with realistic scenarios
- **`tests/check_batching.py`** - Verify and monitor batching effectiveness
- **Triton Metrics** - `http://localhost:8002/metrics`
- **Triton API** - `http://localhost:8000/v2/...`

---

## Next Steps

- **[Model Setup Guide](MODEL_SETUP.md)** - Add more models
- **[API Guide](API_GUIDE.md)** - Understand Triton API endpoints
- **[Troubleshooting](TROUBLESHOOTING.md)** - Fix common issues
- **[Triton Logging](TRITON_LOGGING_GUIDE.md)** - Debug with logs

---

**Happy Testing! 🚀**
